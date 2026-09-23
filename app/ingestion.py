import json

from .cache import redis_client


QUEUE_NAME = "trace_ingestion_queue"


def enqueue_trace(trace_data: dict):
    redis_client.rpush(
        QUEUE_NAME,
        json.dumps(trace_data)
    )