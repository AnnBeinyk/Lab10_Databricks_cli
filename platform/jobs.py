import time
from .api import call_api
from .config import CONFIG

def get_job_by_name(name: str):
    result = call_api("GET", "/api/2.1/jobs/list")

    for job in result.get("jobs", []):
        job_name = job.get("settings", {}).get("name")
        if job_name == name:
            return job.get("job_id")

    return None

def create_or_update_job(cluster_id: str,  notebook_path: str = None) -> int:
    path = notebook_path or CONFIG.notebook_path
    job_name="beinyk-api-job"

    print(f"Using notebook: {path}")
    print(f"Job name: {job_name}")

    payload = {
        "name": job_name,
        "tasks": [
            {
                "task_key": "run_notebook",
                "existing_cluster_id": cluster_id,
                "notebook_task": {
                    "notebook_path": path
                }
            }
        ]
    }

    existing_job_id = get_job_by_name(job_name)
    if existing_job_id:
        print(f"Updating existing job: {existing_job_id}")

        call_api(
            "POST",
            "/api/2.1/jobs/update",
            {
                "job_id": existing_job_id,
                "new_settings": payload
            }
        )

        return existing_job_id

    else:
        print("Creating new job")

        result = call_api("POST", "/api/2.1/jobs/create", payload)
        return result["job_id"]


def run_job(job_id: int) -> int:
    result = call_api("POST", "/api/2.1/jobs/run-now", {"job_id": job_id})
    return result["run_id"]


def monitor_run(run_id: int, poll_interval: int = 20) -> str:
    while True:
        result = call_api("GET", f"/api/2.1/jobs/runs/get?run_id={run_id}")

        state = result.get("state", {})
        life_cycle = state.get("life_cycle_state")
        result_state = state.get("result_state")

        print(f"Run status: {life_cycle} | Result: {result_state}")

        if life_cycle in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
            return result_state or "UNKNOWN"

        time.sleep(poll_interval)


def trigger_pipeline(pipeline_id: str, full_refresh: bool = False) -> str:
    payload = {
        "full_refresh": full_refresh
    }

    result = call_api(
        "POST",
        f"/api/2.0/pipelines/{pipeline_id}/updates",
        payload
    )

    return result["update_id"]



def monitor_pipeline(pipeline_id: str, update_id: str, poll_interval: int = 20):
    while True:
        result = call_api(
            "GET",
            f"/api/2.0/pipelines/{pipeline_id}/updates/{update_id}"
        )

        update = result.get("update", {})
        state = update.get("state")
        if not state:
            raise Exception(f"Unexpected response: {result}")
        print(f"Pipeline state: {state}")

        if state in ["COMPLETED", "FAILED", "CANCELED"]:
            return state

        time.sleep(poll_interval)