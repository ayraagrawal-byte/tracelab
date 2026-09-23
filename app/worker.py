import json
from sqlalchemy.exc import IntegrityError
from .cache import redis_client
from .database import SessionLocal
from .logging_config import get_logger
from .models import Trace
from .metrics import (
    duplicate_traces_total,
    trace_duration_ms,
    traces_processed_total,
)
from prometheus_client import start_http_server

QUEUE_NAME = "trace_ingestion_queue"

logger = get_logger(__name__)


def process_trace(trace_data: dict):
    db = SessionLocal()

    try:
        db_trace = Trace(**trace_data)

        db.add(db_trace)
        db.commit()
        traces_processed_total.inc()
        trace_duration_ms.observe(trace_data["duration_ms"])

        logger.info(
            "Trace saved",
            extra={
                "trace_id": trace_data["trace_id"],
                "service_name": trace_data["service_name"],
                "duration_ms": trace_data["duration_ms"]
            }
        )

    except IntegrityError:
        db.rollback()
        duplicate_traces_total.inc()

        logger.warning(
            "Duplicate trace skipped",
            extra={
                "trace_id": trace_data["trace_id"],
                "service_name": trace_data["service_name"]
            }
        )

    finally:
        db.close()


def run_worker():
    start_http_server(8001)

    logger.info("TraceLab worker started")

    while True:
        item = redis_client.blpop(
            QUEUE_NAME,
            timeout=0
        )

        if item:
            _, trace_json = item

            trace_data = json.loads(trace_json)

            process_trace(trace_data)


if __name__ == "__main__":
    run_worker()