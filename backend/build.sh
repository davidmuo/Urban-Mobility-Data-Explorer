#!/usr/bin/env bash
set -o errexit
pip install --prefer-binary -r requirements.txt
python -c "
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    from app.models import Trip
    if Trip.query.count() == 0:
        import pandas as pd
        df = pd.read_csv('data/processed/cleaned_trips.csv', nrows=10000)
        df = df.rename(columns={'VendorID':'vendor_id','RatecodeID':'ratecode_id','PULocationID':'pulocation_id','DOLocationID':'dolocation_id'})
        df.to_sql('trips', db.engine, if_exists='append', index=False)
        print('Loaded', len(df), 'trips')
    else:
        print('Database already has', Trip.query.count(), 'trips')
"
