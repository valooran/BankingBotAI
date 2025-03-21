import sys
import os

# Add backend/app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.database import Base, engine
from app.models.user import User
from app.models.account import Account


Base.metadata.create_all(bind=engine)
print("Tables created successfully!")