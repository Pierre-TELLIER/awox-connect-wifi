from logging import error

import requests

L4HAPI_URL = "https://l4hapi-prod.awox.cloud/api"


class ApiClient:
    def __init__(self, session: requests.Session):
        self.session = session

    def exchange_for_jwt(self, parse_token: str) -> dict:
        try:
            response = self.session.get(
                f"{L4HAPI_URL}/user/login/token",
                json={
                    "token": parse_token,
                    "duration": 3600,
                },
                headers={
                    "User-Agent": "awox-connect-wifi",
                },
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error(f"JWT exchange failed: HTTP {response.status_code}: {response.text}")
            raise

        except requests.exceptions.RequestException as e:
            error(f"JWT exchange request failed: {e}")
            raise

        except ValueError as e:
            error(f"JWT exchange returned invalid JSON: {e}")
            raise

    def provision_device_certificate(
            self,
            jwt_token: str,
            device_uuid: str,
            csr_pem: str,
    ) -> dict:
        try:
            response = self.session.post(
                f"{L4HAPI_URL}/forgery/deviceCertificate",
                json={
                    "deviceUuid": device_uuid,
                    "csr": csr_pem,
                    "track": 0,
                    "deviceFwVersion": "2.0.0",
                },
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "User-Agent": "awox-connect-wifi",
                },
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error(
                f"Device certificate provisioning failed: "
                f"HTTP {response.status_code}: {response.text}"
            )
            raise

        except requests.exceptions.RequestException as e:
            error(f"Device certificate provisioning request failed: {e}")
            raise

        except ValueError as e:
            error(
                f"Device certificate provisioning returned invalid JSON: {e}"
            )
            raise
