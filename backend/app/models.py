from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

from app.extensions import db

class Zone(db.Model):
    __tablename__ = 'zones'
    
    location_id = db.Column(db.Integer, primary_key=True)
    borough = db.Column(db.String(50))
    zone = db.Column(db.String(100))
    service_zone = db.Column(db.String(50))
    
    pickup_trips = db.relationship('Trip', foreign_keys='Trip.pulocation_id', backref='pickup_zone')
    dropoff_trips = db.relationship('Trip', foreign_keys='Trip.dolocation_id', backref='dropoff_zone')
    
    def to_dict(self):
        return {
            'location_id': self.location_id,
            'borough': self.borough,
            'zone': self.zone,
            'service_zone': self.service_zone
        }


class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    
    vendor_id = db.Column(db.Integer)
    pickup_datetime = db.Column(db.DateTime, nullable=False)
    dropoff_datetime = db.Column(db.DateTime, nullable=False)
    passenger_count = db.Column(db.Integer)
    trip_distance = db.Column(db.Float)
    ratecode_id = db.Column(db.Integer)
    store_and_fwd_flag = db.Column(db.String(1))
    pulocation_id = db.Column(db.Integer, db.ForeignKey('zones.location_id'))
    dolocation_id = db.Column(db.Integer, db.ForeignKey('zones.location_id'))
    payment_type = db.Column(db.Integer)
    fare_amount = db.Column(db.Float)
    extra = db.Column(db.Float)
    mta_tax = db.Column(db.Float)
    tip_amount = db.Column(db.Float)
    tolls_amount = db.Column(db.Float)
    improvement_surcharge = db.Column(db.Float)
    total_amount = db.Column(db.Float)
    congestion_surcharge = db.Column(db.Float)
    
    trip_duration_minutes = db.Column(db.Float)
    trip_speed_mph = db.Column(db.Float)         
    fare_per_mile = db.Column(db.Float)          
    is_weekend = db.Column(db.Boolean)           
    time_of_day_category = db.Column(db.String(20))  
    
    __table_args__ = (
        db.Index('idx_pickup_datetime', 'pickup_datetime'),
        db.Index('idx_pulocation', 'pulocation_id'),
        db.Index('idx_dolocation', 'dolocation_id'),
        db.Index('idx_vendor', 'vendor_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'pickup_datetime': self.pickup_datetime.isoformat() if self.pickup_datetime else None,
            'dropoff_datetime': self.dropoff_datetime.isoformat() if self.dropoff_datetime else None,
            'passenger_count': self.passenger_count,
            'trip_distance': self.trip_distance,
            'pulocation_id': self.pulocation_id,
            'dolocation_id': self.dolocation_id,
            'payment_type': self.payment_type,
            'fare_amount': self.fare_amount,
            'tip_amount': self.tip_amount,
            'tolls_amount': self.tolls_amount,
            'total_amount': self.total_amount,
            'trip_duration_minutes': self.trip_duration_minutes,
            'trip_speed_mph': self.trip_speed_mph,
            'fare_per_mile': self.fare_per_mile,
            'is_weekend': self.is_weekend,
            'time_of_day_category': self.time_of_day_category
        }