import os
from app import app
from extensions import db

print("Current working directory:", os.getcwd())  # Ye line add karo

with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")
