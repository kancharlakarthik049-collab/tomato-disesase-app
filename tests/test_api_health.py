import requests


def test_health():
    resp = requests.get('http://localhost:5000/health')
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('status') == 'ok'
