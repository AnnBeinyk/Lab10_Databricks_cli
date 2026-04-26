import argparse
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


def main():
    parser = argparse.ArgumentParser(description="Databricks Platform CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- cluster ---
    subparsers.add_parser("cluster")

    # --- job ---
    job_parser = subparsers.add_parser("job")
    job_parser.add_argument("--notebook-path", required=False)

    # --- run job ---
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--job-id", type=int, required=False)

    # --- pipeline ---
    pipe_parser = subparsers.add_parser("pipeline")
    pipe_parser.add_argument("--pipeline-id", required=False)

    # --- full flow ---
    subparsers.add_parser("full")

    args = parser.parse_args()

    # ===== COMMANDS =====

    if args.command == "cluster":
        cluster_id = create_or_get_cluster()
        ensure_cluster_running(cluster_id)
        print(f"Cluster ready: {cluster_id}")

    elif args.command == "job":
        cluster_id = create_or_get_cluster()
        ensure_cluster_running(cluster_id)

        job_id = create_or_update_job(cluster_id, args.notebook_path)
        print(f"Job ready: {job_id}")

    elif args.command == "run":
        if args.job_id:
            job_id = args.job_id
        else:
            cluster_id = create_or_get_cluster()
            ensure_cluster_running(cluster_id)
            job_id = create_or_update_job(cluster_id)

        run_id = run_job(job_id)
        print(f"Run started: {run_id}")

        status = monitor_run(run_id)
        print(f"Final status: {status}")

    elif args.command == "pipeline":
        pipeline_id = args.pipeline_id or CONFIG.pipeline_id

        if not pipeline_id:
            raise ValueError("Pipeline ID is not provided")

        update_id = trigger_pipeline(pipeline_id)
        print(f"Pipeline started: {update_id}")

        status = monitor_pipeline(pipeline_id, update_id)
        print(f"Pipeline status: {status}")

    elif args.command == "full":
        cluster_id = create_or_get_cluster()
        ensure_cluster_running(cluster_id)

        job_id = create_or_update_job(cluster_id)
        run_id = run_job(job_id)

        status = monitor_run(run_id)

        if status != "SUCCESS":
            raise RuntimeError("Job failed")

        if CONFIG.pipeline_id:
            update_id = trigger_pipeline(CONFIG.pipeline_id)
            monitor_pipeline(CONFIG.pipeline_id, update_id)

        print("Full pipeline completed successfully")


if __name__ == "__main__":
    main()