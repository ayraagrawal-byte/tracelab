from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="TraceLab",
    description="Distributed request tracing and observability platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "name": "TraceLab",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/v1/traces", response_model=schemas.TraceResponse)
@app.post(
    "/api/v1/traces",
    response_model=schemas.TraceResponse,
    status_code=201
)
def create_trace(
    trace: schemas.TraceCreate,
    db: Session = Depends(get_db)
):
    existing_trace = (
        db.query(models.Trace)
        .filter(models.Trace.trace_id == trace.trace_id)
        .first()
    )

    if existing_trace:
        raise HTTPException(
            status_code=409,
            detail=f"Trace '{trace.trace_id}' already exists"
        )

    db_trace = models.Trace(
        trace_id=trace.trace_id,
        service_name=trace.service_name,
        operation_name=trace.operation_name,
        start_time=trace.start_time,
        duration_ms=trace.duration_ms,
        status=trace.status
    )

    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)

    return db_trace
# Get one specific trace
@app.get(
    "/api/v1/traces/{trace_id}",
    response_model=schemas.TraceResponse
)
def get_trace(
    trace_id: str,
    db: Session = Depends(get_db)
):
    trace = (
        db.query(models.Trace)
        .filter(models.Trace.trace_id == trace_id)
        .first()
    )

    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' not found"
        )

    return trace


# Get and filter multiple traces
@app.get(
    "/api/v1/traces",
    response_model=list[schemas.TraceResponse]
)
def get_traces(
    service_name: str | None = None,
    status: str | None = None,
    min_duration_ms: float | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Trace)

    if service_name:
        query = query.filter(
            models.Trace.service_name == service_name
        )

    if status:
        query = query.filter(
            models.Trace.status == status
        )

    if min_duration_ms is not None:
        query = query.filter(
            models.Trace.duration_ms >= min_duration_ms
        )

    query = query.order_by(
        models.Trace.start_time.desc()
    )

    return query.offset(offset).limit(limit).all()

@app.post(
    "/api/v1/spans",
    response_model=schemas.SpanResponse,
    status_code=201
)
def create_span(
    span: schemas.SpanCreate,
    db: Session = Depends(get_db)
):
    # Make sure the trace exists
    trace = (
        db.query(models.Trace)
        .filter(models.Trace.trace_id == span.trace_id)
        .first()
    )

    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{span.trace_id}' not found"
        )

    # Make sure the span_id is unique
    existing_span = (
        db.query(models.Span)
        .filter(models.Span.span_id == span.span_id)
        .first()
    )

    if existing_span:
        raise HTTPException(
            status_code=409,
            detail=f"Span '{span.span_id}' already exists"
        )

    # Only check for a parent if this span actually has one
    if span.parent_span_id:
        parent_span = (
            db.query(models.Span)
            .filter(
                models.Span.span_id == span.parent_span_id
            )
            .first()
        )

        if not parent_span:
            raise HTTPException(
                status_code=404,
                detail=f"Parent span '{span.parent_span_id}' not found"
            )

        if parent_span.trace_id != span.trace_id:
            raise HTTPException(
                status_code=400,
                detail="Parent span belongs to a different trace"
            )

    # Create the span
    db_span = models.Span(
        span_id=span.span_id,
        trace_id=span.trace_id,
        parent_span_id=span.parent_span_id,
        service_name=span.service_name,
        operation_name=span.operation_name,
        start_time=span.start_time,
        duration_ms=span.duration_ms,
        status=span.status
    )

    db.add(db_span)
    db.commit()
    db.refresh(db_span)

    return db_span

@app.get(
    "/api/v1/traces/{trace_id}/spans",
    response_model=list[schemas.SpanResponse]
)
def get_trace_spans(
    trace_id: str,
    db: Session = Depends(get_db)
):
    # Make sure the trace exists
    trace = (
        db.query(models.Trace)
        .filter(models.Trace.trace_id == trace_id)
        .first()
    )

    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Trace '{trace_id}' not found"
        )

    # Find every span belonging to this trace
    spans = (
        db.query(models.Span)
        .filter(models.Span.trace_id == trace_id)
        .all()
    )

    return spans

@app.get(
    "/api/v1/traces",
    response_model=list[schemas.TraceResponse]
)
def get_traces(
    service_name: str | None = None,
    status: str | None = None,
    min_duration_ms: float | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Trace)

    if service_name:
        query = query.filter(
            models.Trace.service_name == service_name
        )

    if status:
        query = query.filter(
            models.Trace.status == status
        )

    if min_duration_ms is not None:
        query = query.filter(
            models.Trace.duration_ms >= min_duration_ms
        )

    return query.all()
