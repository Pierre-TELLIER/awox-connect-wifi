import uuid
from logging import info, error

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from awox.api.client import ApiClient
from awox.config import AppConfig
from awox.parse.client import ParseClient
from awox.state import AppState, DeviceConfig, save_certificates, save_state, Device, DeviceState


def generate_keypair_and_csr() -> tuple[str, str]:
    """
    Generate an EC P-256 private key and a CSR using the AwoX
    certificate subject template.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Occitanie"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Montpellier"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Awox"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT Department"),
        x509.NameAttribute(NameOID.COMMON_NAME, "awox.cloud"),
    ])

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(private_key, hashes.SHA256())
    )

    csr_pem = csr.public_bytes(
        serialization.Encoding.PEM
    ).decode("ascii")

    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")

    return key_pem, csr_pem


class Provisioner:
    def __init__(
            self,
            config: AppConfig,
            state: AppState,
    ):
        self.config = config
        self.state = state
        self.session = requests.Session()

    def provision(self) -> AppState:
        if self.state.provisioned:
            info("Already provisioned.")
            return self.state

        username = self.config.awox.username
        password = self.config.awox.password
        my_udn = str(uuid.uuid4())
        key_pem, csr_pem = generate_keypair_and_csr()
        gateware = f"Gateware_{uuid.uuid4()}"

        info("[1/5] Parse login...")
        parse_client = ParseClient(
            username,
            password,
            self.session,
        )

        info("[2/5] Exchanging Parse session for JWT + l4h cookie + certificates")

        api_client = ApiClient(self.session)

        auth = api_client.exchange_for_jwt(
            parse_client.session_token()
        )

        jwt_token = auth["jwtToken"]
        device_cert_prov = api_client.provision_device_certificate(
            jwt_token,
            gateware,
            csr_pem,
        )

        save_certificates(
            self.config.storage.certificate_directory,
            device_cert=device_cert_prov["deviceCert"],
            device_key=key_pem,
            ca_cert=device_cert_prov["caCert"],
            root_ca=device_cert_prov["rootCa"],
        )
        info(
            f"      userId={auth.get('userId')} "
            f"account={auth.get('account')}"
        )

        info(
            "[4/5] Generating our own keypair + CSR, "
            "provisioning a new AWS IoT identity..."
        )

        info("[3/5] Fetching devices...")

        devices = parse_client.devices()
        compatible_devices = [
            device for device in devices
            if ".wifi.light" in device.get("type")
        ]

        if len(compatible_devices) == 0:
            error(f"No devices found. {devices}")
            exit(1)

        for target in compatible_devices:
            account_id = target["owner"]["objectId"]
            bridge_gateware_id = f"gw{target['macAddress'].replace(':', '').upper()}"
            device_id = f"{target['provider']}_{target['uuid']}"
            friendly_name = target.get("friendlyName")

            device_config = DeviceConfig(
                friendly_name=friendly_name,
                account_id=account_id,
                bridge_gateware_id=bridge_gateware_id,
                device_id=device_id,
                device_uuid=gateware,
                udn=my_udn,
                fingerprint=device_cert_prov["fingerprint"],
                mqtt_endpoint=device_cert_prov["mqttEndPoint"],
            )

            self.state.devices[device_id] = Device(config=device_config, state=DeviceState())

        self.state.provisioned = True

        save_state(
            self.config.storage.state_file,
            self.state,
        )

        return self.state
