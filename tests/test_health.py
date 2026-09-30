def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["database"] == "up"


def test_unknown_route_uses_error_envelope(client):
    r = client.get("/api/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "http_error"
