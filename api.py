import os
import requests

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type": "application/json"
}


def call_api(method, endpoint, payload=None):
    url = f"{DATABRICKS_HOST}{endpoint}"

    response = requests.request(method, url, headers=HEADERS, json=payload)

    if not response.ok:
        raise Exception(f"API error {response.status_code}: {response.text}")

    return response.json()