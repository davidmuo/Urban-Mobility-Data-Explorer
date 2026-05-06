from app import create_app, db
from app.models import Zone, Trip 

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created from models!")
    