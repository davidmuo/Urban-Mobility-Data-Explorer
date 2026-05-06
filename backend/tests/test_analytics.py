def test_top_routes_returns_200(client):
    res = client.get("/api/analytics/top-routes")
    assert res.status_code == 200


def test_top_routes_structure(client):
    data = client.get("/api/analytics/top-routes").get_json()
    assert "top_routes" in data
    assert "algorithm" in data
    assert "total_analyzed" in data


def test_top_routes_each_has_route_and_count(client):
    routes = client.get("/api/analytics/top-routes").get_json()["top_routes"]
    assert len(routes) > 0
    for r in routes:
        assert "route" in r
        assert "count" in r


def test_top_routes_limit(client):
    data = client.get("/api/analytics/top-routes?limit=1").get_json()
    assert len(data["top_routes"]) <= 1


def test_top_routes_total_analyzed_matches_data(client):
    data = client.get("/api/analytics/top-routes").get_json()
    assert data["total_analyzed"] == 10
