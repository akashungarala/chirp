from app import schemas
from fastapi import status

def test_health_check(client):
    """
    Verify the /health endpoint:
    - Returns 200 OK
    - Reports service status, uptime, version, and database connectivity
    """
    response = client.get("/health/")
    assert response.status_code == status.HTTP_200_OK
    health_status = schemas.HealthStatus(**response.json())
    # Validate service status
    assert health_status.status == "ok"
    assert health_status.uptime_seconds >= 0
    # Validate application version
    assert health_status.version == "1.0.0"
    # Validate database connectivity status
    assert health_status.database == schemas.DatabaseStatus.connected