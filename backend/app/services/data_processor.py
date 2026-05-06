import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.cleaning_log = []
        self.original_count = 0
        self.cleaned_count = 0

    def load_data(self, trips_path, zones_path):
        logger.info("Loading trips data...")

        if trips_path.endswith('.parquet'):
            self.trips_df = pd.read_parquet(trips_path)
        else:
            self.trips_df = pd.read_csv(trips_path)

        self.original_count = len(self.trips_df)
        logger.info(f"Loaded {self.original_count} raw trips")

        logger.info("Loading zones lookup...")
        self.zones_df = pd.read_csv(zones_path)

        return self.trips_df, self.zones_df

    def clean_data(self):
        print("Columns found:", self.trips_df.columns.tolist())

        self.trips_df = self.trips_df.rename(columns={
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime'
        })

        before = len(self.trips_df)
        self.trips_df = self.trips_df.dropna(subset=['PULocationID', 'DOLocationID'])
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with null location IDs")

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['passenger_count'] > 0]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with zero passengers")

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['fare_amount'] > 0]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with invalid fares")

        self.trips_df['pickup_datetime'] = pd.to_datetime(self.trips_df['pickup_datetime'])
        self.trips_df['dropoff_datetime'] = pd.to_datetime(self.trips_df['dropoff_datetime'])

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['dropoff_datetime'] > self.trips_df['pickup_datetime']]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with invalid time order")

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['trip_distance'] > 0]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with zero/negative distance")

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['trip_distance'] < 200]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with unrealistic distance (>200mi)")

        before = len(self.trips_df)
        self.trips_df = self.trips_df[self.trips_df['fare_amount'] < 500]
        self._log_cleaning(f"Removed {before - len(self.trips_df)} rows with unrealistic fare (>$500)")

        self.cleaned_count = len(self.trips_df)
        return self.trips_df

    def engineer_features(self):
        duration = self.trips_df['dropoff_datetime'] - self.trips_df['pickup_datetime']
        self.trips_df['trip_duration_minutes'] = duration.dt.total_seconds() / 60

        mask = self.trips_df['trip_duration_minutes'] > 0
        self.trips_df['trip_speed_mph'] = 0.0
        self.trips_df.loc[mask, 'trip_speed_mph'] = (
            self.trips_df.loc[mask, 'trip_distance'] /
            (self.trips_df.loc[mask, 'trip_duration_minutes'] / 60)
        )

        mask = self.trips_df['trip_distance'] > 0
        self.trips_df['fare_per_mile'] = 0.0
        self.trips_df.loc[mask, 'fare_per_mile'] = (
            self.trips_df.loc[mask, 'fare_amount'] /
            self.trips_df.loc[mask, 'trip_distance']
        )

        self.trips_df['is_weekend'] = self.trips_df['pickup_datetime'].dt.dayofweek >= 5

        hour = self.trips_df['pickup_datetime'].dt.hour
        conditions = [
            (hour >= 5) & (hour < 12),
            (hour >= 12) & (hour < 17),
            (hour >= 17) & (hour < 21),
            (hour >= 21) | (hour < 5)
        ]
        choices = ['Morning', 'Afternoon', 'Evening', 'Night']
        self.trips_df['time_of_day_category'] = np.select(conditions, choices, default='Unknown')

        logger.info("Feature engineering complete")
        return self.trips_df

    def _log_cleaning(self, message):
        self.cleaning_log.append(message)
        logger.info(message)

    def get_cleaning_summary(self):
        return {
            'original_rows': self.original_count,
            'cleaned_rows': self.cleaned_count,
            'removed_rows': self.original_count - self.cleaned_count,
            'removal_percentage': (self.original_count - self.cleaned_count) / self.original_count * 100,
            'cleaning_steps': self.cleaning_log
        }