def test_get_zones_returns_200(client):
    res = client.get("/api/zones/")
    assert res.status_code == 200


def test_get_zones_structure(client):
    data = client.get("/api/zones/").get_json()
    assert "zones" in data
    assert "total" in data


def test_get_zones_count(client):
    data = client.get("/api/zones/").get_json()
    assert data["total"] == 2


def test_get_zone_by_id(client):
    data = client.get("/api/zones/1").get_json()
    assert data["location_id"] == 1
    assert data["borough"] == "Manhattan"
    assert data["zone"] == "Midtown Center"


def test_get_zone_fields(client):
    data = client.get("/api/zones/2").get_json()
    for field in ("location_id", "borough", "zone", "service_zone"):
        assert field in data


def test_get_zone_not_found(client):
    res = client.get("/api/zones/9999")
    assert res.status_code == 404
    assert "error" in res.get_json()
