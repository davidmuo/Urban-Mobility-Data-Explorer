import pytest
from datetime import datetime
from app import create_app
from app.extensions import db as _db
from app.models import Zone, Trip


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        _db.create_all()
        _seed()
        yield app
        _db.drop_all()


def _seed():
    zone1 = Zone(location_id=1, borough="Manhattan", zone="Midtown Center", service_zone="Yellow Zone")
    zone2 = Zone(location_id=2, borough="Brooklyn", zone="Downtown Brooklyn", service_zone="Boro Zone")
    _db.session.add_all([zone1, zone2])

    for i in range(10):
        trip = Trip(
            pickup_datetime=datetime(2019, 1, 1 + i % 7, 8, 0),
            dropoff_datetime=datetime(2019, 1, 1 + i % 7, 8, 30),
            passenger_count=1,
            trip_distance=2.5 + i,
            pulocation_id=1,
            dolocation_id=2,
            fare_amount=10.0 + i,
            total_amount=12.0 + i,
            trip_duration_minutes=30.0,
            trip_speed_mph=5.0,
            fare_per_mile=4.0,
            is_weekend=False,
            time_of_day_category="Morning",
        )
        _db.session.add(trip)
    _db.session.commit()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()
