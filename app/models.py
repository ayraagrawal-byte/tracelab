from sqlalchemy import Column, DateTime, Float, Integer, String
from .database import Base


class Trace(Base):
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, index=True)

    trace_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    service_name = Column(
        String,
        nullable=False
    )

    operation_name = Column(
        String,
        nullable=False
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    duration_ms = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

class Span(Base):
    __tablename__ = "spans"

    id = Column(Integer, primary_key=True, index=True)

    span_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    trace_id = Column(
        String,
        index=True,
        nullable=False
    )

    parent_span_id = Column(
        String,
        nullable=True
    )

    service_name = Column(
        String,
        nullable=False
    )

    operation_name = Column(
        String,
        nullable=False
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    duration_ms = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )    