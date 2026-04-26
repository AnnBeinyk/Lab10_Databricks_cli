
from .api import call_api
from .config import CONFIG
import time

def get_cluster_by_name(name: str):
    endpoint = "/api/2.0/clusters/list"

    while endpoint:
        result = call_api("GET", endpoint)

        for cluster in result.get("clusters", []):
            if cluster.get("cluster_name") == name:
                return {
                    "cluster_id": cluster.get("cluster_id"),
                    "state": cluster.get("state")
                }

        next_token = result.get("next_page_token")
        if next_token:
            endpoint = f"/api/2.0/clusters/list?page_token={next_token}"
        else:
            endpoint = None

    return None

def create_or_get_cluster(cluster_name="beinyk_api_Cluster")->str:
    existing = get_cluster_by_name(cluster_name)

    if existing:
        print(f"Found cluster: {existing.get('cluster_id')} | State: {existing.get('state')}")
        cluster_id = existing.get("cluster_id")

        if not cluster_id:
            raise Exception("Cluster found but cluster_id is missing")

        return cluster_id

    print(f"Creating new cluster: {cluster_name}")
    payload = {
        "cluster_name": cluster_name,
        "spark_version": "17.3.x-scala2.13",

        "spark_conf": {
            "spark.master": "local[*]",
            "spark.databricks.cluster.profile": "singleNode"
        },

        "node_type_id": "Standard_F4",
        "driver_node_type_id": "Standard_F4",

        "num_workers": 0,

        "azure_attributes": {
            "first_on_demand": 1,
            "availability": "ON_DEMAND_AZURE",
            "spot_bid_max_price": -1
        },

        "custom_tags": {
            "ResourceClass": "SingleNode",
            "owner": CONFIG.email
        },

        "autotermination_minutes": 15,
        "enable_elastic_disk": True,
        "enable_local_disk_encryption": False,

        "data_security_mode": "USER_ISOLATION",
        "runtime_engine": "STANDARD",

        "apply_policy_default_values": False
    }

    result = call_api("POST", "/api/2.0/clusters/create", payload)
    cluster_id = result["cluster_id"]
    print(f"Created cluster: {cluster_id}")
    return cluster_id

def get_cluster_state(cluster_id: str) -> str:
    result = call_api("GET", f"/api/2.0/clusters/get?cluster_id={cluster_id}")
    return result.get("state")

def start_cluster(cluster_id: str):
    print(f"Starting cluster: {cluster_id}")
    call_api("POST", "/api/2.0/clusters/start", {"cluster_id": cluster_id})


def wait_for_cluster(cluster_id: str, poll_interval: int = 20):
    while True:
        state = get_cluster_state(cluster_id)
        print(f"Cluster state: {state}")

        if state == "RUNNING":
            return
        elif state in ["ERROR", "TERMINATED"]:
            raise Exception(f"Cluster failed: {state}")

        time.sleep(poll_interval)

def ensure_cluster_running(cluster_id: str):
    state = get_cluster_state(cluster_id)
    print(f"Initial cluster state: {state}")

    if state == "RUNNING":
        print("Cluster already running")
        return

    if state in ["TERMINATED", "ERROR"]:
        start_cluster(cluster_id)

    wait_for_cluster(cluster_id)