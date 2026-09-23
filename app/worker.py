import json

from .cache import redis_client
from .database import SessionLocal
from .models import Trace
from sqlalchemy.exc import IntegrityError


QUEUE_NAME = "trace_ingestion_queue"
def process_trace(trace_data: dict):
    db = SessionLocal()

    try:
        db_trace = Trace(**trace_data)

        db.add(db_trace)
        db.commit()

        print(
            f"Saved trace: {trace_data['trace_id']}"
        )

    except IntegrityError:
        db.rollback()

        print(
            f"Skipped duplicate trace: {trace_data['trace_id']}"
        )

    finally:
        db.close()

def run_worker():
    print("TraceLab worker started...")

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