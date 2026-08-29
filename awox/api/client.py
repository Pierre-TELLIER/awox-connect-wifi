import json

import requests

L4HAPI_URL = "https://l4hapi-prod.awox.cloud/api"

class ApiClient:
    def __init__(self, session: requests.Session):
        self.session = session


    def exchange_for_jwt(self, parse_token: str) -> dict:
        body = json.dumps({"token": parse_token, "duration": 3600})
        resp = self.session.request(
            "GET",
            f"{L4HAPI_URL}/user/login/token",
            data=body,
            headers={"User-Agent": "AwoX", "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


    def provision_device_certificate(self, jwt_token: str, device_uuid: str, csr_pem: str) -> dict:
        resp = self.session.post(
            f"{L4HAPI_URL}/forgery/deviceCertificate",
            json={
                "deviceUuid": device_uuid,
                "csr": csr_pem,
                "track": 0,
                "deviceFwVersion": "2.0.0",
            },
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "User-Agent": "AwoX",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        return resp.json()