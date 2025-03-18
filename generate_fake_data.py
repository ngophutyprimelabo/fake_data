import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker
import sys
import json
import argparse
from check_display import update_display_flag

from core.database import get_db, engine, Base
from models import (
    User, Personnel, Organization, Conversation, 
    Message, Tag, MessageTag, Userprompt, EmployeeType, FieldMapping, RoleType, OrganizationType
)
# Import predefined values
from value import role_type, employee_type, organization_type

SET_LOCALE="ja"

# Initialize Faker with multiple locales
fake_en = Faker('en_US')
fake_ja = Faker('ja_JP')  # Japanese locale
fake = fake_en  # Default to English

def set_locale(locale='en'):
    """Set the locale for faker data generation."""
    global fake
    if (locale == 'ja'):
        fake = fake_ja
        print("Using Japanese locale for data generation")
    else:
        fake = fake_en
        print("Using English locale for data generation")

def create_tables():
    """Create tables in database if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def generate_role_types(db):
    """Generate role type records from predefined values."""
    print("Generating role types...")
    
    inserted_count = 0
    for rt in role_type:
        try:
            role = RoleType(role_type=rt)
            db.add(role)
            db.commit()
            inserted_count += 1
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting role type: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} role types")
    return inserted_count

def generate_employee_types(db):
    """Generate employee type records from predefined values."""
    print("Generating employee types...")
    
    inserted_count = 0
    for et in employee_type:
        try:
            emp_type = EmployeeType(employee_type=et)
            db.add(emp_type)
            db.commit()
            inserted_count += 1
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting employee type: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} employee types")
    return inserted_count

def generate_organization_types(db):
    """Generate organization type records from predefined values."""
    print("Generating organization types...")
    
    inserted_count = 0
    for ot in organization_type:
        try:
            org_type = OrganizationType(organization_type=ot)
            db.add(org_type)
            db.commit()
            inserted_count += 1
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting organization type: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} organization types")
    return inserted_count

def generate_field_mappings(db):
    """Generate field mapping records from predefined values."""
    print("Generating field mappings...")
    
    # Import predefined values for field and field_detail
    from value import field, field_detail
    
    if len(field) != len(field_detail):
        print("Error: field and field_detail arrays must have the same length")
        return 0
    
    inserted_count = 0
    for i in range(len(field)):
        try:
            field_mapping = FieldMapping(
                field=field[i],
                field_detail=field_detail[i]
            )
            db.add(field_mapping)
            db.commit()
            inserted_count += 1
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting field mapping: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} field mappings")
    return inserted_count

def generate_organizations(db, count=500):
    """Generate organization records."""
    print(f"Generating {count} organizations...")
    
    # Import predefined values for field and field_detail
    from value import field, field_detail
    
    # Japanese organization types if Japanese locale is selected
    ja_regions = ["東京", "大阪", "名古屋", "福岡", "札幌", "仙台", "広島", "京都", None]
    
    inserted_count = 0
    for _ in range(count):
        try:
            dept_code = fake.unique.bothify(text="?####")
            division_code = fake.bothify(text="###")
            section_code = fake.bothify(text="##")
            
            # Select a random index to get matching field and field_detail pairs
            field_index = random.randint(0, len(field) - 1)
            
            if fake == fake_ja:
                # Japanese data
                org = Organization(
                    external_department_code=dept_code,
                    external_division_code=division_code,
                    external_section_code=section_code,
                    field=field[field_index],  # Use the predefined field value
                    field_detail=field_detail[field_index],  # Use the matching field_detail value
                    region=random.choice(ja_regions),
                    branch=random.choice([fake.city(), None]),
                    abbreviation=random.choice([fake.first_kana_name()[:2], None]),
                    created_at=fake.date_time_between(start_date='-2y', end_date='now')
                )
            else:
                # English data
                org = Organization(
                    external_department_code=dept_code,
                    external_division_code=division_code,
                    external_section_code=section_code,
                    field=field[field_index],  # Use the predefined field value
                    field_detail=field_detail[field_index],  # Use the matching field_detail value
                    region=random.choice([fake.country(), None]),
                    branch=random.choice([fake.city(), None]),
                    abbreviation=random.choice([fake.language_code(), None]),
                    created_at=fake.date_time_between(start_date='-2y', end_date='now')
                )
            db.add(org)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} organizations")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting organization: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} organizations")
    return inserted_count

def generate_personnel(db, count=400):
    """Generate personnel records."""
    print(f"Generating {count} personnel records...")
    
    # Get available department codes
    dept_codes = [org.external_department_code for org in db.query(Organization).all()]
    if not dept_codes:
        print("No organizations found. Please generate organizations first.")
        return 0
    
    inserted_count = 0
    # We'll store usernames here to use in the generate_users function
    personnel_usernames = []
    
    for _ in range(count):
        try:
            username = fake.unique.user_name()
            personnel_usernames.append(username)
            
            personnel = Personnel(
                external_username=username,
                entry_year=random.randint(1980, 2025),
                department_code=random.choice(dept_codes),
                branch_code=fake.bothify(text="###"),
                head_office_name=fake.company(),
                branch_name=fake.city(),
                section_name=fake.company_prefix() if fake == fake_ja else fake.bs(),
                sales_office_name=random.choice([fake.company_suffix(), None]),
                organization_type=random.choice(organization_type),
                employee_type=random.choice(employee_type),
                role_type=random.choice(role_type),
                is_organization_head=random.choice(["はい", "いいえ"]) if fake == fake_ja else random.choice(["Yes", "No"]),
                is_department_head=random.choice(["はい", "いいえ"]) if fake == fake_ja else random.choice(["Yes", "No"])
            )
            db.add(personnel)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} personnel")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting personnel: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} personnel")
    return inserted_count

def generate_users(db, count=500):
    """Generate user records."""
    print(f"Generating {count} users...")
    
    # Get available personnel usernames that don't have users yet
    personnel = db.query(Personnel).all()
    personnel_usernames = [p.external_username for p in personnel]
    
    inserted_count = 0
    
    # First, create users for all existing personnel (internal users)
    for username in personnel_usernames:
        try:
            user = User(
                external_id=1000 + inserted_count,
                external_id_delete_flag=random.choice([True, False]),
                username=username,  # Use the exact personnel username
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            db.add(user)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count} users")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting user: {str(e)}")
    
    # Then create additional users without personnel data (external users)
    remaining = count - inserted_count
    if remaining > 0:
        print(f"Creating {remaining} additional external users...")
        for i in range(remaining):
            try:
                # External user - generate new unique username
                username = fake.unique.user_name()
                
                user = User(
                    external_id=1000 + inserted_count + i,
                    external_id_delete_flag=random.choice([True, False]),
                    username=username,
                    created_at=fake.date_time_between(start_date='-2y', end_date='now')
                )
                db.add(user)
                db.commit()
                inserted_count += 1
                if inserted_count % 50 == 0:
                    print(f"Inserted {inserted_count}/{count} users")
            except IntegrityError:
                db.rollback()
            except Exception as e:
                db.rollback()
                print(f"Error inserting user: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} users")
    return inserted_count

def generate_conversations(db, count=500):
    """Generate conversation records."""
    print(f"Generating {count} conversations...")
    
    # Get available users
    users = db.query(User).all()
    if not users:
        print("No users found. Please generate users first.")
        return 0
    
    # Japanese models if Japanese locale is selected
    ja_models = [1, 2, 3, 4]  # Model IDs for Japanese models
    en_models = [5, 6, 7, 8]  # Model IDs for English models
    
    inserted_count = 0
    for i in range(count):
        try:
            # Pick a random user
            user = random.choice(users)
            
            # Check if user has associated personnel data
            is_internal = user.personnel is not None
            
            # Generate topic based on locale
            if fake == fake_ja:
                topic = "対話 " + str(i + 1) + ": " + fake.bs()
                model_id = random.choice(ja_models)
            else:
                topic = "Conversation " + str(i + 1) + ": " + fake.bs()
                model_id = random.choice(en_models)
            
            # Create conversation with display_flag based on user type
            # If user is internal (has personnel), display_flag should be False
            # If user is external (no personnel), display_flag should be True
            conversation = Conversation(
                external_id=2000 + i,
                user_id=user.external_id,
                topic=topic,
                created_at=fake.date_time_between(start_date='-3m', end_date='now'),
                model_id=model_id,
                display_flag=not is_internal  # Set display_flag to True for external users, False for internal users
            )
            db.add(conversation)
            db.commit()
            inserted_count += 1
            
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} conversations")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting conversation: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} conversations")
    return inserted_count

def generate_messages(db, count=500):
    """Generate message records."""
    print("Generating messages for conversations...")
    
    # Get available conversations and users
    conversations = db.query(Conversation).all()
    users = db.query(User).all()
    
    if not conversations or not users:
        print("No conversations or users found. Please generate them first.")
        return 0
    
    # Japanese models if Japanese locale is selected
    ja_models = ["gpt-3.5-turbo-ja", "gpt-4-ja", "claude-3-sonnet-ja"]
    en_models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
    
    inserted_count = 0
    # Generate messages for each conversation, ensuring at least 2 messages per conversation
    for conversation in conversations:
        # Generate between 2 and 10 pairs of messages (user + bot)
        message_pairs = random.randint(1, 5)  # Will result in 2-10 total messages
        
        # Get user associated with this conversation
        user = db.query(User).filter(User.external_id == conversation.user_id).first()
        if not user:
            continue
        
        current_time = conversation.created_at
            
        # Generate pairs of user and bot messages for this conversation
        for pair in range(message_pairs):
            try:
                # Create fake chat parameters
                if fake == fake_ja:
                    # Japanese models
                    chat_params = {
                        "temperature": round(random.uniform(0.1, 1.0), 2),
                        "max_tokens": random.randint(50, 2000),
                        "model": random.choice(ja_models)
                    }
                else:
                    # English models
                    chat_params = {
                        "temperature": round(random.uniform(0.1, 1.0), 2),
                        "max_tokens": random.randint(50, 2000),
                        "model": random.choice(en_models)
                    }
                
                # 1. First add user message
                if pair > 0:  # Not the first message pair
                    # Gap between previous bot response and next user question (1-10 minutes)
                    current_time += timedelta(minutes=random.randint(1, 10))
                
                user_message = Message(
                    external_id=3000 + inserted_count,
                    conversation_id=conversation.external_id,
                    message=fake.paragraph(),
                    is_bot=False,  # User message
                    sender_id=user.external_id,
                    chat_parameter=chat_params,
                    created_at=current_time
                )
                db.add(user_message)
                db.commit()
                inserted_count += 1
                
                # 2. Then add bot response (5-30 seconds after user message)
                current_time += timedelta(seconds=random.randint(5, 30))
                
                bot_message = Message(
                    external_id=3000 + inserted_count,
                    conversation_id=conversation.external_id,
                    message=fake.paragraph(nb_sentences=3),
                    is_bot=True,  # Bot message
                    sender_id=user.external_id,
                    chat_parameter=chat_params,
                    created_at=current_time
                )
                db.add(bot_message)
                db.commit()
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    print(f"Inserted {inserted_count} messages")
            except IntegrityError:
                db.rollback()
            except Exception as e:
                db.rollback()
                print(f"Error inserting message: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} messages across {len(conversations)} conversations")
    return inserted_count

def generate_tags(db, count=500):
    """Generate tag records."""
    print(f"Generating {count} tags...")
    
    # Generate Japanese tags if Japanese locale is selected
    if fake == fake_ja:
        # For Japanese, we'll use a predefined set of common Japanese tags
        ja_common_tags = [
            "技術", "ビジネス", "科学", "健康", "教育", "政治", "経済", "スポーツ",
            "エンターテイメント", "食品", "旅行", "ファッション", "テクノロジー", "自動車",
            "金融", "芸術", "音楽", "映画", "書籍", "ゲーム"
        ]
        # Combine with generated words for more variety
        tag_words = ja_common_tags + [fake.word() for _ in range(500)]
        tag_names = set(tag_words[:count])
    else:
        # For English, continue using the faker library
        tag_names = set()
        while len(tag_names) < count:
            tag_names.add(fake.word())
    
    inserted_count = 0
    for tag_name in tag_names:
        try:
            tag = Tag(
                name=tag_name,
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            db.add(tag)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} tags")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting tag: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} tags")
    return inserted_count

def generate_message_tags(db, count=500):
    """Generate message tag connections."""
    print(f"Generating {count} message tags...")
    
    # Get available messages and tags
    messages = db.query(Message).all()
    tags = db.query(Tag).all()
    
    if not messages or not tags:
        print("No messages or tags found. Please generate them first.")
        return 0
    
    inserted_count = 0
    for _ in range(count):
        try:
            message = random.choice(messages)
            tag = random.choice(tags)
            
            message_tag = MessageTag(
                message_id=message.external_id,
                tag_id=tag.id,
                created_at=fake.date_time_between(
                    start_date=message.created_at,
                    end_date='now'
                )
            )
            db.add(message_tag)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} message tags")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting message tag: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} message tags")
    return inserted_count

def generate_userprompts(db, count=500):
    """Generate user prompt records."""
    print(f"Generating {count} user prompts...")
    
    # Get available users
    users = db.query(User).all()
    
    inserted_count = 0
    for i in range(count):
        try:
            # Some prompts may not be associated with a user
            user = random.choice(users + [None] * 50) if users else None
            
            userprompt = Userprompt(
                external_id=4000 + i,
                title=fake.sentence(nb_words=4),
                prompt=fake.paragraph(nb_sentences=3),
                user_id=user.external_id if user else None
            )
            db.add(userprompt)
            db.commit()
            inserted_count += 1
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count}/{count} user prompts")
        except IntegrityError:
            db.rollback()
        except Exception as e:
            db.rollback()
            print(f"Error inserting user prompt: {str(e)}")
    
    print(f"Successfully inserted {inserted_count} user prompts")
    return inserted_count

def generate_all_fake_data(locale='en'):
    """Generate fake data for all models."""
    # Set locale for data generation
    set_locale(locale)
    
    db = next(get_db())
    
    # Uncomment the RoleType model in models.py first before proceeding
    print("First, ensure that you've uncommented the RoleType model in models.py")
    
    try:
        # Create tables if they don't exist
        create_tables()
        
        # Generate data in the correct order to maintain relationships
        generate_role_types(db)
        generate_employee_types(db)
        generate_organization_types(db)
        generate_field_mappings(db)
        generate_organizations(db)
        generate_personnel(db)
        generate_users(db)
        generate_conversations(db)
        generate_messages(db)
        generate_tags(db)
        generate_message_tags(db)
        generate_userprompts(db)
        
        print(f"Successfully generated all fake data in {locale} locale!")
        
    except Exception as e:
        print(f"Error generating fake data: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fake data for database.")
    parser.add_argument("--locale", choices=["en", "ja"], default=SET_LOCALE, 
                        help="Locale for generating data (en=English, ja=Japanese)")
    args = parser.parse_args()
    
    print(f"Starting fake data generation in {args.locale} locale...")
    generate_all_fake_data(args.locale)
    update_display_flag()
    print("Fake data generation completed.")
