import uuid
from logging import info, debug

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from awox.api.client import ApiClient
from awox.config import AppConfig
from awox.parse.client import ParseClient
from awox.state import AppState, DeviceState, save_certificates, save_state


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

        info("[1/5] Parse login...")
        parse_client = ParseClient(
            username,
            password,
            self.session,
        )

        info("[2/5] Fetching devices...")
        devices = parse_client.devices()

        target_device_name = self.config.awox.target_device_name

        target = next(
            (
                device
                for device in devices
                if device.get("friendlyName") == target_device_name
            ),
            None,
        )

        if target is None:
            available = [
                device.get("friendlyName")
                for device in devices
            ]

            raise RuntimeError(
                f"Device '{target_device_name}' not found. "
                f"Available: {available}"
            )

        account_id = target["owner"]["objectId"]
        bridge_gateware_id = (
                "gw"
                + target["macAddress"].replace(":", "").upper()
        )
        device_id = f"{target['provider']}_{target['uuid']}"

        debug(f"      account={account_id}")
        debug(
            f"      device={target['friendlyName']} "
            f"device_id={device_id}"
        )
        debug(
            f"      bridge_gateware_id={bridge_gateware_id}"
        )

        info("[3/5] Exchanging Parse session for JWT + l4h cookie...")

        api_client = ApiClient(self.session)

        auth = api_client.exchange_for_jwt(
            parse_client.session_token()
        )

        jwt_token = auth["jwtToken"]

        info(
            f"      userId={auth.get('userId')} "
            f"account={auth.get('account')}"
        )

        info(
            "[4/5] Generating our own keypair + CSR, "
            "provisioning a new AWS IoT identity..."
        )

        my_device_uuid = f"Gateware_{uuid.uuid4()}"

        key_pem, csr_pem = generate_keypair_and_csr()

        result = api_client.provision_device_certificate(
            jwt_token,
            my_device_uuid,
            csr_pem,
        )

        info("[5/5] Generating our own UDN and saving everything...")

        my_udn = str(uuid.uuid4())

        save_certificates(
            self.config.storage.certificate_directory,
            device_cert=result["deviceCert"],
            device_key=key_pem,
            ca_cert=result["caCert"],
            root_ca=result["rootCa"],
        )

        device_state = DeviceState(
            account_id=account_id,
            bridge_gateware_id=bridge_gateware_id,
            device_id=device_id,
            device_uuid=my_device_uuid,
            udn=my_udn,
            fingerprint=result["fingerprint"],
            mqtt_endpoint=result["mqttEndPoint"],
        )

        self.state.devices[device_id] = device_state
        self.state.provisioned = True

        save_state(
            self.config.storage.state_file,
            self.state,
        )

        return self.state
