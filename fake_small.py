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
import itertools

# Initialize Faker
fake = Faker('ja_JP')
# Add more locales if needed for more diverse fake data
fake_others = [Faker('en_US'), Faker('zh_CN'), Faker('ko_KR')]

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

        # Generate Organizations (100 records instead of 500)
        print("Generating organizations...")
        organizations = []
        for _ in range(100):
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
        print(f"Created {len(organizations)} organizations")

        # Generate Personnel (400 records instead of 5000)
        print("Generating personnel...")
        personnel_list = []
        total_personnel = 400
        
        # First, ensure all abbreviations are used at least once
        remaining_abbrs = abbreviation.copy()
        initial_records = min(len(remaining_abbrs), 100)  # Limit initial records to 100
        
        # Create one record for each abbreviation (up to 100)
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
        batch_size = 100
        remaining_count = total_personnel - initial_records
        
        for batch_start in range(0, remaining_count, batch_size):
            batch_end = min(batch_start + batch_size, remaining_count)
            print(f"Generating personnel batch {batch_start}-{batch_end} of {remaining_count}...")
            
            for _ in range(batch_end - batch_start):
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
        
        print(f"Created {len(personnel_list)} personnel records")

        # Generate Users (1000 records instead of 15000)
        print("Generating users...")
        users = []
        user_batch_size = 200
        internal_user_count = len(personnel_list)
        external_user_count = 1000 - internal_user_count
        
        # Track used usernames to ensure uniqueness
        used_usernames = set()
        
        # Create internal users from personnel records (in batches)
        for batch_start in range(0, internal_user_count, user_batch_size):
            batch_end = min(batch_start + user_batch_size, internal_user_count)
            print(f"Generating internal users batch {batch_start}-{batch_end} of {internal_user_count}...")
            
            batch_personnel = personnel_list[batch_start:batch_end]
            for personnel in batch_personnel:
                # Determine if this is a valid internal user based on your criteria
                is_internal = True
                
                # Check organization_type is not None and role_type is not in EXCLUDE_ROLE_TYPE
                if personnel.organization_type is None or personnel.role_type in EXCLUDE_ROLE_TYPE:
                    is_internal = False
                
                # Store username in the set to track used names
                used_usernames.add(personnel.external_username)
                    
                user = User(
                    external_id=1000 + len(users),
                    external_id_delete_flag=random.choice([True, False]),
                    username=personnel.external_username,
                    internal_user_flag=is_internal,  # Set based on our criteria
                    created_at=fake.date_time_between(start_date='-2y', end_date='now')
                )
                users.append(user)
                db.add(user)
            db.commit()
        
        # Add external users (not in personnel system) - in batches
        for batch_start in range(0, external_user_count, user_batch_size):
            batch_end = min(batch_start + user_batch_size, external_user_count)
            print(f"Generating external users batch {batch_start}-{batch_end} of {external_user_count}...")
            
            for i in range(batch_end - batch_start):
                # Cycle through faker instances more frequently to avoid exhausting any single one
                faker_idx = i % len(fake_others)
                faker_instance = fake_others[faker_idx]
                
                # Create more variation in username generation
                if i % 4 == 0:
                    # Standard username
                    base_username = faker_instance.user_name()
                elif i % 4 == 1:
                    # Username with digit suffix
                    base_username = f"{faker_instance.first_name().lower()}_{random.randint(1, 9999)}"
                elif i % 4 == 2:
                    # Username with word
                    base_username = f"{faker_instance.first_name().lower()}_{faker_instance.word()}"
                else:
                    # Completely custom pattern
                    base_username = f"{faker_instance.lexify('??')}_{faker_instance.bothify('###?')}"
                
                # Ensure uniqueness by adding suffixes if needed
                username = base_username
                attempt = 0
                while username in used_usernames:
                    attempt += 1
                    username = f"{base_username}_{attempt}"
                    # If we're still having trouble, add more randomness
                    if attempt > 5:
                        username = f"{base_username}_{random.randint(1000, 9999)}"
                
                # Add to our tracking set
                used_usernames.add(username)
                
                user = User(
                    external_id=1000 + len(users),
                    external_id_delete_flag=random.choice([True, False]),
                    username=username,
                    internal_user_flag=False,  # External users
                    created_at=faker_instance.date_time_between(start_date='-2y', end_date='now')
                )
                users.append(user)
                db.add(user)
            db.commit()
        
        print(f"Created {len(users)} user records")

        # Generate Conversations (2500 records instead of 25000)
        print("Generating conversations...")
        conversations = []
        num_conversations = 2500
        conv_batch_size = 500
        
        for batch_start in range(0, num_conversations, conv_batch_size):
            batch_end = min(batch_start + conv_batch_size, num_conversations)
            print(f"Generating conversations {batch_start}-{batch_end} of {num_conversations}...")
            
            for i in range(batch_start, batch_end):
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
            
            # Commit after each batch
            db.commit()
            # Clear conversations list to free memory after committing
            conversations = []
                
        db.commit()
        print(f"Created {num_conversations} conversations")

        # Generate Messages (10,000 records instead of 30,000)
        print("Generating messages...")
        message_count = 0
        target_message_count = 10000
        messages_per_batch = 500
        
        # Create a set to track used external_ids
        used_message_ids = set()
        
        # Or use a counter as a guaranteed unique ID source
        id_counter = itertools.count(10000000)
        
        # Calculate approximately how many messages per conversation we need
        avg_messages_per_conversation = target_message_count // num_conversations
        # Make sure it's an even number (for user-bot pairs)
        if avg_messages_per_conversation % 2 == 1:
            avg_messages_per_conversation += 1
        
        print(f"Target: ~{avg_messages_per_conversation} messages per conversation")
        
        # Fetch conversations in batches to save memory
        for conv_batch_start in range(0, num_conversations, 250):
            conv_batch_end = min(conv_batch_start + 250, num_conversations)
            print(f"Fetching conversations {conv_batch_start}-{conv_batch_end}...")
            
            # Get a batch of conversations from database
            conv_batch = db.query(Conversation).filter(
                Conversation.external_id >= (2000 + conv_batch_start),
                Conversation.external_id < (2000 + conv_batch_end)
            ).all()
            
            for conv_idx, conv in enumerate(conv_batch):
                # Skip if we've reached our target
                if message_count >= target_message_count:
                    break
                    
                # Report progress periodically
                if conv_idx % 50 == 0:
                    print(f"Generating messages for conversation batch {conv_batch_start+conv_idx}... Total messages so far: {message_count}")
                
                # Randomize messages per conversation around the average
                pairs = max(2, min(20, int(random.normalvariate(avg_messages_per_conversation//2, 3))))
                
                current_time = conv.created_at
                
                # Randomly select a category for this conversation
                category_choice = random.choice(insurance_categories)
                _, category_group_label,_, main_category_label,_, chat_parameter_category_label = category_choice
                
                # Batch for this conversation
                batch_msgs = []
                
                for _ in range(pairs):
                    # User message
                    chat_params = {
                        "temperature": round(random.uniform(0.1, 1.0), 2),
                        "max_tokens": random.randint(50, 2000),
                        "model": random.choice(["gpt-3.5-turbo-ja", "gpt-4-ja", "claude-3-sonnet-ja"])
                    }
                    
                    # Get a guaranteed unique ID using the counter
                    external_id = next(id_counter)
                    
                    batch_msgs.append(Message(
                        external_id=external_id,
                        conversation_id=conv.external_id,
                        message=fake.paragraph(),
                        is_bot=False,
                        chat_parameter=chat_params,
                        main_category=main_category_label,
                        category_group=category_group_label,
                        chat_parameter_category=chat_parameter_category_label,
                        created_at=current_time
                    ))
                    message_count += 1
                    
                    # Bot response (30-50 seconds later)
                    current_time += timedelta(seconds=random.randint(30, 50))
                    
                    # Get next unique ID
                    external_id = next(id_counter)
                    
                    batch_msgs.append(Message(
                        external_id=external_id,
                        conversation_id=conv.external_id,
                        message=fake.paragraph(),
                        is_bot=True,
                        chat_parameter=chat_params,
                        main_category=main_category_label,
                        category_group=category_group_label,
                        chat_parameter_category=chat_parameter_category_label,
                        created_at=current_time
                    ))
                    message_count += 1
                    
                    # Add delay before next pair
                    current_time += timedelta(minutes=random.randint(1, 10))
                
                # Add all messages for this conversation
                for msg in batch_msgs:
                    db.add(msg)
                
                # Commit every batch_size messages to avoid huge transactions
                if message_count % messages_per_batch < len(batch_msgs):
                    db.commit()
                    print(f"Committed batch of messages. Total: {message_count}")
                
        # Final commit for any remaining messages
        db.commit()
        print(f"Created {message_count} message records")

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

def update_flags_based_on_types():
    """
    Update display_flag in conversations and internal_user_flag in users 
    to False when associated with role_types or employee_types with flag=0
    """
    from sqlalchemy import or_
    
    db = next(get_db())
    try:
        print("Updating flags based on role and employee types...")
        
        # Get role types and employee types with flag = 0
        role_types_zero_flag = [rt.role_type for rt in db.query(RoleType).filter(RoleType.roletype_display_flag == 0).all()]
        employee_types_zero_flag = [et.employee_type for et in db.query(EmployeeType).filter(EmployeeType.employeetype_display_flag == 0).all()]
        
        print(f"Found {len(role_types_zero_flag)} role types and {len(employee_types_zero_flag)} employee types with flag=0")
        
        # If none have flag = 0, nothing to do
        if not role_types_zero_flag and not employee_types_zero_flag:
            print("No role types or employee types with flag = 0 found.")
            return
            
        # Get personnel with these role types or employee types
        filter_conditions = []
        if role_types_zero_flag:
            filter_conditions.append(Personnel.role_type.in_(role_types_zero_flag))
        if employee_types_zero_flag:
            filter_conditions.append(Personnel.employee_type.in_(employee_types_zero_flag))
            
        personnel_query = db.query(Personnel).filter(or_(*filter_conditions))
        
        personnel_list = personnel_query.all()
        print(f"Found {len(personnel_list)} personnel with zero-flagged role or employee types")
        
        # Get the usernames of these personnel
        usernames = [p.external_username for p in personnel_list]
        
        # Get the corresponding users
        users = db.query(User).filter(User.username.in_(usernames)).all()
        print(f"Found {len(users)} users associated with these personnel")
        
        updated_user_count = 0
        updated_conversation_count = 0
        
        # Update each matching user and their conversations
        for user in users:
            # Skip if already set to False
            if not user.internal_user_flag:
                continue
                
            # Update user flag
            user.internal_user_flag = False
            updated_user_count += 1
            
            # Update all their conversations
            conversations = db.query(Conversation).filter(
                Conversation.user_id == user.external_id,
                Conversation.display_flag == True  # Only update those currently True
            ).all()
            
            for conv in conversations:
                conv.display_flag = False
                updated_conversation_count += 1
        
        db.commit()
        print(f"Updated {updated_user_count} users and {updated_conversation_count} conversations")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating flags based on types: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    # generate_data()
    # Run validation to ensure all flags are properly set
    # update_display_flags()
    update_flags_based_on_types()
