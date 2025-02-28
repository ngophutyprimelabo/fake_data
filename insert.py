import sys
from sqlalchemy.exc import IntegrityError

from connect import get_db, engine, Base
from models import RoleType

def create_tables():
    """Create tables in database if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
if __name__ == "__main__":
    print("Starting database setup...")
    create_tables()
    print("Database setup completed.")