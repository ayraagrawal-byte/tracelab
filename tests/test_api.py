def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "TraceLab",
        "version": "0.1.0"
    }

def test_create_and_get_trace(client):
    trace_data = {
        "trace_id": "test-trace-001",
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 725.5,
        "status": "OK"
    }

    # Create the trace
    response = client.post(
        "/api/v1/traces",
        json=trace_data
    )

    assert response.status_code == 201

    created_trace = response.json()

    assert created_trace["trace_id"] == "test-trace-001"
    assert created_trace["service_name"] == "checkout-service"
    assert created_trace["duration_ms"] == 725.5

    # Get the trace back
    response = client.get(
        "/api/v1/traces/test-trace-001"
    )

    assert response.status_code == 200

    fetched_trace = response.json()

    assert fetched_trace["trace_id"] == "test-trace-001"
    assert fetched_trace["operation_name"] == "POST /checkout"

def test_duplicate_trace(client):
    trace_data = {
        "trace_id": "duplicate-trace",
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 500,
        "status": "OK"
    }

    # First request should succeed
    first_response = client.post(
        "/api/v1/traces",
        json=trace_data
    )

    assert first_response.status_code == 201

    # Same trace_id again should fail
    second_response = client.post(
        "/api/v1/traces",
        json=trace_data
    )

    assert second_response.status_code == 409


def test_trace_not_found(client):
    response = client.get(
        "/api/v1/traces/does-not-exist"
    )

    assert response.status_code == 404   

def test_create_span(client):
    # First create a trace
    trace_data = {
        "trace_id": "span-test-trace",
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 800,
        "status": "OK"
    }

    trace_response = client.post(
        "/api/v1/traces",
        json=trace_data
    )

    assert trace_response.status_code == 201

    # Now create a span belonging to that trace
    span_data = {
        "span_id": "span-test-001",
        "trace_id": "span-test-trace",
        "parent_span_id": None,
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 800,
        "status": "OK"
    }

    span_response = client.post(
        "/api/v1/spans",
        json=span_data
    )

    assert span_response.status_code == 201

    created_span = span_response.json()

    assert created_span["span_id"] == "span-test-001"
    assert created_span["trace_id"] == "span-test-trace"
    assert created_span["parent_span_id"] is None

def test_span_requires_existing_trace(client):
    span_data = {
        "span_id": "orphan-span",
        "trace_id": "trace-does-not-exist",
        "parent_span_id": None,
        "service_name": "payment-service",
        "operation_name": "POST /charge",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 200,
        "status": "OK"
    }

    response = client.post(
        "/api/v1/spans",
        json=span_data
    )

    assert response.status_code == 404    

def test_parent_child_spans(client):
    # Create trace
    client.post(
        "/api/v1/traces",
        json={
            "trace_id": "parent-test-trace",
            "service_name": "checkout-service",
            "operation_name": "POST /checkout",
            "start_time": "2026-09-22T16:00:00",
            "duration_ms": 800,
            "status": "OK"
        }
    )

    # Create parent span
    parent_response = client.post(
        "/api/v1/spans",
        json={
            "span_id": "parent-span",
            "trace_id": "parent-test-trace",
            "parent_span_id": None,
            "service_name": "checkout-service",
            "operation_name": "POST /checkout",
            "start_time": "2026-09-22T16:00:00",
            "duration_ms": 800,
            "status": "OK"
        }
    )

    assert parent_response.status_code == 201

    # Create child span
    child_response = client.post(
        "/api/v1/spans",
        json={
            "span_id": "child-span",
            "trace_id": "parent-test-trace",
            "parent_span_id": "parent-span",
            "service_name": "payment-service",
            "operation_name": "POST /charge",
            "start_time": "2026-09-22T16:00:01",
            "duration_ms": 300,
            "status": "OK"
        }
    )

    assert child_response.status_code == 201
    assert child_response.json()["parent_span_id"] == "parent-span"   

def test_invalid_parent_span(client):
    # Create trace
    client.post(
        "/api/v1/traces",
        json={
            "trace_id": "invalid-parent-trace",
            "service_name": "checkout-service",
            "operation_name": "POST /checkout",
            "start_time": "2026-09-22T16:00:00",
            "duration_ms": 500,
            "status": "OK"
        }
    )

    # Try creating a child whose parent does not exist
    response = client.post(
        "/api/v1/spans",
        json={
            "span_id": "child-span",
            "trace_id": "invalid-parent-trace",
            "parent_span_id": "fake-parent",
            "service_name": "payment-service",
            "operation_name": "POST /charge",
            "start_time": "2026-09-22T16:00:01",
            "duration_ms": 200,
            "status": "OK"
        }
    )

    assert response.status_code == 404

def test_trace_is_cached(client):
    trace_data = {
        "trace_id": "cached-trace",
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-22T16:00:00",
        "duration_ms": 600,
        "status": "OK"
    }

    # Create the trace
    response = client.post(
        "/api/v1/traces",
        json=trace_data
    )

    assert response.status_code == 201

    # Retrieve it, which should put it in Redis
    response = client.get(
        "/api/v1/traces/cached-trace"
    )

    assert response.status_code == 200

    # Check that Redis now contains it
    from app.cache import redis_client

    cached_trace = redis_client.get(
        "trace:cached-trace"
    )

    assert cached_trace is not None

def test_ingest_trace_adds_to_queue(client):
    trace_data = {
        "trace_id": "queued-trace",
        "service_name": "checkout-service",
        "operation_name": "POST /checkout",
        "start_time": "2026-09-23T01:00:00",
        "duration_ms": 500,
        "status": "OK"
    }

    response = client.post(
        "/api/v1/traces/ingest",
        json=trace_data
    )

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert response.json()["trace_id"] == "queued-trace"

    from app.cache import redis_client

    queued_trace = redis_client.lpop(
        "trace_ingestion_queue"
    )

    assert queued_trace is not None                      