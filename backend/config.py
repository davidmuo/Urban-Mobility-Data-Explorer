import os

class Config:
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')

    if DB_TYPE == 'postgres':
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/nyc_db'
        )
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nyc_taxi.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-key-for-nyc-taxi'