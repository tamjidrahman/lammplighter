from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@patch("api.main.lammps", __version__=0)
def test_version(mock_lammps):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"lammps_version": mock_lammps.__version__}
