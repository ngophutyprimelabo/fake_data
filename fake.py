import random
from datetime import datetime, timedelta
from faker import Faker
from core.database import get_db, engine, Base
from models import (
    User, Personnel, Organization, Conversation,
    Message, RoleType, EmployeeType,
    FieldMapping, Abbreviation, CategoryMapping
)
from value import role_type, employee_type, abbreviation, FIELD_MAPPING, insurance_categories, EXCLUDE_ROLE_TYPE

# Initialize Faker
fake = Faker('ja_JP')

def create_tables():
    """Create all tables in database"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

def generate_data():
    db = next(get_db())
    try:
        # Create tables
        create_tables()
        
        # Insert Role Types
        print("Generating role types...")
        for rt in role_type:
            if not db.query(RoleType).filter(RoleType.role_type == rt).first():
                db.add(RoleType(role_type=rt))
        db.commit()
        
        # Insert Employee Types
        print("Generating employee types...")
        for et in employee_type:
            if not db.query(EmployeeType).filter(EmployeeType.employee_type == et).first():
                db.add(EmployeeType(employee_type=et))
        db.commit()
        
        # Define org_types for use later (without creating DB records)
        org_types = ["本社", "営業", "各支店", "その他"]
        
        # Insert Insurance Categories
        print("Generating category mappings...")
        for category_group, category_group_label, main_category, main_category_label, chat_parameter_category, chat_parameter_category_label in insurance_categories:
            db.add(CategoryMapping(
                category_group=category_group,
                category_group_label=category_group_label,
                main_category=main_category,
                main_category_label=main_category_label,
                chat_parameter_category=chat_parameter_category,
                chat_parameter_category_label=chat_parameter_category_label
            ))
        db.commit()

        # Insert Field Mappings
        print("Generating field mappings...")
        for field, field_detail in FIELD_MAPPING:
            if not db.query(FieldMapping).filter(FieldMapping.field_detail == field_detail).first():
                db.add(FieldMapping(field=field, field_detail=field_detail))
        db.commit()

        # Insert Abbreviations
        print("Generating abbreviations...")
        for abbr in abbreviation:
            if not db.query(Abbreviation).filter(Abbreviation.abbreviation == abbr).first():
                db.add(Abbreviation(abbreviation=abbr))
        db.commit()

        # Generate Organizations (200 records)
        print("Generating organizations...")
        organizations = []
        for _ in range(200):
            field_map = random.choice(FIELD_MAPPING)  # Random field mapping tuple
            org = Organization(
                external_department_code=fake.unique.bothify(text="?####"),
                external_division_code=fake.bothify(text="###"),
                external_section_code=fake.bothify(text="##"),
                field=field_map[0],
                field_detail=field_map[1],
                region=random.choice(["東京", "大阪", "名古屋", "福岡", "札幌", "仙台", "広島", "京都"]),
                branch=fake.city(),
                abbreviation=random.choice(abbreviation),
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            organizations.append(org)
            db.add(org)
        db.commit()

        # Generate Personnel (300 records)
        print("Generating personnel...")
        personnel_list = []
        total_personnel = 300
        
        # First, ensure all abbreviations are used at least once
        remaining_abbrs = abbreviation.copy()
        initial_records = len(remaining_abbrs)
        
        # Create one record for each abbreviation
        for abbr in remaining_abbrs[:initial_records]:
            personnel = Personnel(
                external_username=fake.unique.user_name(),
                entry_year=random.randint(1980, 2025),
                department_code=random.choice([org.external_department_code for org in organizations]),
                branch_code=fake.bothify(text="###"),
                head_office_name=fake.company(),
                branch_name=abbr,  # Use each abbreviation exactly once
                section_name=fake.company_suffix(),
                sales_office_name=fake.company_suffix(),
                organization_type=random.choice(org_types),
                employee_type=random.choice(employee_type),
                role_type=random.choice(role_type),
                is_organization_head=random.choice(["はい", "いいえ"]),
                is_department_head=random.choice(["はい", "いいえ"])
            )
            personnel_list.append(personnel)
            db.add(personnel)
        
        # Generate remaining records with random abbreviations
        for _ in range(total_personnel - initial_records):
            personnel = Personnel(
                external_username=fake.unique.user_name(),
                entry_year=random.randint(1980, 2025),
                department_code=random.choice([org.external_department_code for org in organizations]),
                branch_code=fake.bothify(text="###"),
                head_office_name=fake.company(),
                branch_name=random.choice(abbreviation),  # Randomly choose from all abbreviations
                section_name=fake.company_suffix(),
                sales_office_name=fake.company_suffix(),
                organization_type=random.choice(org_types),
                employee_type=random.choice(employee_type),
                role_type=random.choice(role_type),
                is_organization_head=random.choice(["はい", "いいえ"]),
                is_department_head=random.choice(["はい", "いいえ"])
            )
            personnel_list.append(personnel)
            db.add(personnel)
        db.commit()

        # Generate Users (500 records)
        print("Generating users...")
        users = []
        
        # Create internal users from personnel records
        for personnel in personnel_list:
            # Determine if this is a valid internal user based on your criteria
            is_internal = True
            
            # Check organization_type is not None and role_type is not in EXCLUDE_ROLE_TYPE
            if personnel.organization_type is None or personnel.role_type in EXCLUDE_ROLE_TYPE:
                is_internal = False
                
            user = User(
                external_id=1000 + len(users),
                external_id_delete_flag=random.choice([True, False]),
                username=personnel.external_username,
                internal_user_flag=is_internal,  # Set based on our criteria
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            users.append(user)
            db.add(user)
        
        # Add some external users (not in personnel system)
        for i in range(200):
            user = User(
                external_id=1000 + len(users),
                external_id_delete_flag=random.choice([True, False]),
                username=fake.unique.user_name(),
                internal_user_flag=False,  # External users
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            users.append(user)
            db.add(user)
        
        db.commit()

        # Generate Conversations (400 records)
        print("Generating conversations...")
        conversations = []
        for i in range(400):
            user = random.choice(users)  # Randomly choosing a user
            
            # Set display_flag based on internal_user_flag
            display_flag = user.internal_user_flag
            
            conversation = Conversation(
                external_id=2000 + i,
                user_id=user.external_id,  # Using the selected user's external_id
                topic=f"対話 {i+1}: {fake.sentence()}",
                created_at=fake.date_time_between(start_date='-3w', end_date=datetime.now() - timedelta(days=1)),
                model_id=random.choice([3, 4, 5]),
                display_flag=display_flag  # Set based on user's internal flag
            )
            conversations.append(conversation)
            db.add(conversation)
        db.commit()

        # Generate Messages (2000 records, ~5 per conversation)
        print("Generating messages...")
        for conv in conversations:
            # Generate 3-7 message pairs per conversation
            pairs = random.randint(3, 7)
            current_time = conv.created_at
            
            # Randomly select a category for this conversation
            category_choice = random.choice(insurance_categories)
            _, category_group_label,_, main_category_label,_, chat_parameter_category_label = category_choice
            
            for _ in range(pairs):
                # User message
                chat_params = {
                    "temperature": round(random.uniform(0.1, 1.0), 2),
                    "max_tokens": random.randint(50, 2000),
                    "model": random.choice(["gpt-3.5-turbo-ja", "gpt-4-ja", "claude-3-sonnet-ja"])
                }
                
                db.add(Message(
                    external_id=fake.unique.random_number(digits=8),
                    conversation_id=conv.external_id,
                    message=fake.paragraph(),
                    is_bot=False,
                    chat_parameter=chat_params,
                    # Add these required fields:
                    main_category=main_category_label,
                    category_group=category_group_label,
                    chat_parameter_category=chat_parameter_category_label,
                    created_at=current_time
                ))
                
                # Bot response (5-30 seconds later)
                current_time += timedelta(seconds=random.randint(30, 50))
                db.add(Message(
                    external_id=fake.unique.random_number(digits=8),
                    conversation_id=conv.external_id,
                    message=fake.paragraph(),
                    is_bot=True,
                    chat_parameter=chat_params,
                    # Add these required fields:
                    main_category=main_category_label,
                    category_group=category_group_label,
                    chat_parameter_category=chat_parameter_category_label,
                    created_at=current_time
                ))
                
                # Add delay before next pair
                current_time += timedelta(minutes=random.randint(1, 10))
        db.commit()

        print("Data generation completed successfully!")

    except Exception as e:
        print(f"Error generating data: {str(e)}")
        db.rollback()
    finally:
        db.close()

# Function to check and update display flags if needed
def update_display_flags():
    db = next(get_db())
    try:
        print("Updating display flags for conversations...")
        
        # Get all users
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            should_display = True
            
            # Check if user has a personnel record
            personnel = db.query(Personnel).filter(Personnel.external_username == user.username).first()
            if not personnel:
                should_display = False
            else:
                # Check if organization_type is null
                if personnel.organization_type is None:
                    should_display = False
                # Check if role_type is in EXCLUDE_ROLE_TYPE
                elif personnel.role_type in EXCLUDE_ROLE_TYPE:
                    should_display = False
            
            # Update all conversations for this user if needed
            if not should_display and user.internal_user_flag:
                # Update user first
                user.internal_user_flag = False
                
                # Get all conversations for this user
                conversations = db.query(Conversation).filter(
                    Conversation.user_id == user.external_id,
                    Conversation.display_flag == True  # Only update those currently set to True
                ).all()
                
                for conversation in conversations:
                    conversation.display_flag = False
                    updated_count += 1
        
        db.commit()
        print(f"Updated display_flag to False for {updated_count} conversations")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating display flags: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_data()
    # Run validation to ensure all flags are properly set
    update_display_flags()
