from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_version():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"lammps_version": 0}
