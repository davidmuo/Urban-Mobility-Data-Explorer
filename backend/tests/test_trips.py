import json


def test_get_trips_returns_200(client):
    res = client.get("/api/trips/")
    assert res.status_code == 200


def test_get_trips_response_structure(client):
    data = client.get("/api/trips/").get_json()
    assert "trips" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data


def test_get_trips_contains_records(client):
    data = client.get("/api/trips/").get_json()
    assert data["total"] == 10
    assert len(data["trips"]) == 10


def test_get_trips_pagination(client):
    data = client.get("/api/trips/?per_page=3").get_json()
    assert len(data["trips"]) == 3
    assert data["pages"] == 4


def test_get_trips_filter_min_fare(client):
    data = client.get("/api/trips/?min_fare=15").get_json()
    for trip in data["trips"]:
        assert trip["fare_amount"] >= 15


def test_get_trips_filter_date(client):
    data = client.get("/api/trips/?start_date=2019-01-05").get_json()
    for trip in data["trips"]:
        assert trip["pickup_datetime"] >= "2019-01-05"


def test_get_trips_trip_fields(client):
    trip = client.get("/api/trips/?per_page=1").get_json()["trips"][0]
    for field in ("id", "pickup_datetime", "fare_amount", "trip_distance",
                  "pulocation_id", "dolocation_id", "trip_duration_minutes"):
        assert field in trip
