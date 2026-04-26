import os
import requests
from .config import CONFIG


HEADERS = {
    "Authorization": f"Bearer {CONFIG.token}",
    "Content-Type": "application/json"
}


def call_api(method, endpoint, payload=None):
    url = f"{CONFIG.host}{endpoint}"

    response = requests.request(method, url, headers=HEADERS, json=payload)
    print(f"[{method}] {endpoint} -> {response.status_code}")
    if not response.ok:
        print(response.text)
        raise Exception(f"API error {response.status_code}: {response.text}")

    return response.json()