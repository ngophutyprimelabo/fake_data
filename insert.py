import sys
from sqlalchemy.exc import IntegrityError

from connect import get_db, engine, Base
from models import RoleType

def create_tables():
    """Create tables in database if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def insert_role_types():
    """Insert sample role types into the role_types table."""
    # Common role types to insert
    role_types = [
        "Manager",
        "Director",
        "Associate",
        "Senior Associate",
        "Vice President",
        "Senior Vice President",
        "Executive Director",
        "Managing Director",
        "Analyst",
        "Senior Analyst",
        "Specialist",
        "Team Lead",
        "Department Head",
        "Supervisor",
        "Consultant",
        "Senior Consultant"
    ]
    
    # Get database session
    db = next(get_db())
    
    # Insert all role types in a single batch
    inserted_count = 0
    role_objects = []
    
    for role in role_types:
        role_objects.append(RoleType(role_type=role))
    
    try:
        db.bulk_save_objects(role_objects)
        db.commit()
        inserted_count = len(role_objects)
        print(f"Inserted {inserted_count} role types")
    except IntegrityError:
        db.rollback()
        print("Error inserting role types in bulk, trying one by one...")
        
        # Fall back to one-by-one insertion with retry logic
        for role in role_types:
            try:
                # Create a new session for each attempt
                db = next(get_db())
                role_type = RoleType(role_type=role)
                db.add(role_type)
                db.commit()
                inserted_count += 1
                print(f"Inserted role type: {role}")
            except IntegrityError:
                db.rollback()
                print(f"Role type '{role}' already exists, skipping.")
            except Exception as e:
                db.rollback()
                print(f"Error inserting '{role}': {str(e)}")
    
    print(f"Successfully inserted {inserted_count} role types.")

if __name__ == "__main__":
    print("Starting database setup...")
    create_tables()
    insert_role_types()
    print("Database setup completed.")