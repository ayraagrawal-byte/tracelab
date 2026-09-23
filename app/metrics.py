from prometheus_client import Counter, Histogram


traces_ingested_total = Counter(
    "tracelab_traces_ingested_total",
    "Total number of traces submitted for ingestion"
)


traces_processed_total = Counter(
    "tracelab_traces_processed_total",
    "Total number of traces successfully processed by the worker"
)


duplicate_traces_total = Counter(
    "tracelab_duplicate_traces_total",
    "Total number of duplicate traces rejected by the worker"
)


trace_duration_ms = Histogram(
    "tracelab_trace_duration_ms",
    "Distribution of trace durations in milliseconds"
)