from datetime import datetime, timezone
from uuid import uuid4

from locust import HttpUser, between, task


class TraceLabUser(HttpUser):
    wait_time = between(0.05, 0.15)

    @task
    def ingest_trace(self):
        trace_id = f"load-{uuid4()}"

        payload = {
            "trace_id": trace_id,
            "service_name": "load-test-service",
            "operation_name": "POST /load-test",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 250.0,
            "status": "OK"
        }

        self.client.post(
            "/api/v1/traces/ingest",
            json=payload,
            name="/api/v1/traces/ingest"
        )