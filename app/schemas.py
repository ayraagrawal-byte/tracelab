from datetime import datetime

from pydantic import BaseModel


class TraceCreate(BaseModel):
    trace_id: str
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    status: str


class TraceResponse(TraceCreate):
    id: int

    model_config = {
        "from_attributes": True
    }

class SpanCreate(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: str | None = None
    service_name: str
    operation_name: str
    start_time: datetime
    duration_ms: float
    status: str


class SpanResponse(SpanCreate):
    id: int

    model_config = {
        "from_attributes": True
    }    