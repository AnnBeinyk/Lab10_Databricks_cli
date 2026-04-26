from platform import (
    create_or_get_cluster,
    ensure_cluster_running,
    create_or_update_job,
    run_job,
    monitor_run,
    trigger_pipeline,
    monitor_pipeline,
)
from platform.config import CONFIG
import time

def safe_run_job(job_id, retries=2):
    for attempt in range(retries):
        try:
            return run_job(job_id)
        except Exception:
            if attempt == retries - 1:
                raise
            print(f"Retrying job run ({attempt + 1})...")
            time.sleep(5)


def validate_config():
    if not CONFIG.notebook_path:
        raise ValueError("DATABRICKS_NOTEBOOK_PATH is not set")

def run_notebook_job(notebook_path=None):
    print("=== Databricks REST API Automation ===")

    print("Step 1: Create or reuse cluster")
    cluster_id = create_or_get_cluster()
    print(f"Cluster ID: {cluster_id}")

    print("Step 2: Ensure cluster is running")
    ensure_cluster_running(cluster_id)

    print("Step 3: Create or update job")
    job_id = create_or_update_job(cluster_id, notebook_path)
    print(f"Job ID: {job_id}")

    print("Step 4: Submit job run")
    run_id = safe_run_job(job_id)
    print(f"Run ID: {run_id}")

    print("Step 5: Monitor job status")
    status = monitor_run(run_id)
    print(f"Job final status: {status}")

    if status != "SUCCESS":
        raise RuntimeError("Databricks job failed")

    print("Notebook job completed successfully")
    return status


def run_dlt_pipeline():

    pipeline_id = CONFIG.pipeline_id
    if not pipeline_id:
        raise ValueError("Pipeline ID is empty")

    print("=== Databricks Pipeline Trigger ===")
    print(f"Pipeline ID: {pipeline_id}")

    update_id = trigger_pipeline(pipeline_id, full_refresh=False)
    print(f"Pipeline update ID: {update_id}")

    status = monitor_pipeline(pipeline_id, update_id)
    print(f"Pipeline final status: {status}")

    if status != "COMPLETED":
        raise Exception("Databricks pipeline failed")

    print("Pipeline completed successfully")


def main():
    validate_config()
    job_status=run_notebook_job()
    if job_status != "SUCCESS":
        raise Exception("Stopping pipeline because job failed")

    if CONFIG.pipeline_id:
        run_dlt_pipeline()
    else:
        print("Skipping DLT pipeline: DATABRICKS_PIPELINE_ID is not set")


if __name__ == "__main__":
    main()