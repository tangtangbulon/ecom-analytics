from fastapi.testclient import TestClient
from main_3 import app


client = TestClient(app)
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_sales_analytics_normal():
    response = client.get("/analytics/sales?start_date=2023-09-20")
    assert response.status_code == 200

def test_get_sales_analytics_bad_date():
    response = client.get("/analytics/sales?start_date=2023-09-20a")
    assert response.status_code == 422