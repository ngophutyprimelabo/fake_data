import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker
import sys
import json
import argparse

from connect import get_db, engine, Base
from models import (
    User, Personnel, Organization, Conversation, 
    Message, Tag, MessageTag, Userprompt
)

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

def generate_organizations(db, count=500):
    """Generate organization records."""
    print(f"Generating {count} organizations...")
    
    # Japanese organization types if Japanese locale is selected
    ja_organization_types = ["企業", "支社", "部門", None]
    ja_regions = ["東京", "大阪", "名古屋", "福岡", "札幌", "仙台", "広島", "京都", None]
    
    inserted_count = 0
    for _ in range(count):
        try:
            dept_code = fake.unique.bothify(text="?####")
            division_code = fake.bothify(text="###")
            section_code = fake.bothify(text="##")
            
            if fake == fake_ja:
                # Japanese data
                org = Organization(
                    external_department_code=dept_code,
                    external_division_code=division_code,
                    external_section_code=section_code,
                    field=random.choice([fake.company_prefix(), None]),
                    field_detail=random.choice([fake.company_suffix(), None]),
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
                    field=random.choice([fake.bs(), None]),
                    field_detail=random.choice([fake.catch_phrase(), None]),
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

def generate_personnel(db, count=500):
    """Generate personnel records."""
    print(f"Generating {count} personnel records...")
    
    # Get available department codes
    dept_codes = [org.external_department_code for org in db.query(Organization).all()]
    if not dept_codes:
        print("No organizations found. Please generate organizations first.")
        return 0
    
    # Japanese specific options if Japanese locale is selected
    ja_organization_types = ["企業", "支社", "部門", None]
    ja_employee_types = ["正社員", "パートタイム", "契約社員", None]
    ja_role_types = ["マネージャー", "ディレクター", "アソシエイト", "アナリスト", None]
    ja_boolean = ["はい", "いいえ", None]
        
    inserted_count = 0
    for _ in range(count):
        try:
            username = fake.unique.user_name()
            
            if fake == fake_ja:
                # Japanese data
                personnel = Personnel(
                    external_username=username,
                    entry_year=random.randint(1980, 2025),
                    department_code=random.choice(dept_codes),
                    branch_code=fake.bothify(text="###"),
                    head_office_name=fake.company(),
                    branch_name=fake.city(),
                    section_name=fake.company_prefix(),
                    sales_office_name=random.choice([fake.company_suffix(), None]),
                    organization_type=random.choice(ja_organization_types),
                    employee_type=random.choice(ja_employee_types),
                    role_type=random.choice(ja_role_types),
                    is_organization_head=random.choice(ja_boolean),
                    is_department_head=random.choice(ja_boolean)
                )
            else:
                # English data
                personnel = Personnel(
                    external_username=username,
                    entry_year=random.randint(1980, 2025),
                    department_code=random.choice(dept_codes),
                    branch_code=fake.bothify(text="###"),
                    head_office_name=fake.company(),
                    branch_name=fake.city(),
                    section_name=fake.bs(),
                    sales_office_name=random.choice([fake.company_suffix(), None]),
                    organization_type=random.choice(["Corporate", "Branch", "Department", None]),
                    employee_type=random.choice(["Full-time", "Part-time", "Contract", None]),
                    role_type=random.choice(["Manager", "Director", "Associate", "Analyst", None]),
                    is_organization_head=random.choice(["Yes", "No", None]),
                    is_department_head=random.choice(["Yes", "No", None])
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
    
    # Get available personnel usernames
    usernames = [p.external_username for p in db.query(Personnel).all()]
    
    if not usernames:
        print("No personnel found. Please generate personnel first.")
        return 0
    
    inserted_count = 0
    for i in range(count):
        try:
            # Ensure username is never None since it's not nullable
            username = random.choice(usernames)
            
            user = User(
                external_id=1000 + i,
                external_id_delete_flag=random.choice([True, False]),
                username=username,  # Always provide a valid username
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
    
    inserted_count = 0
    for i in range(count):
        try:
            conversation = Conversation(
                external_id=2000 + i,
                user_id=random.choice(users).external_id,
                topic=fake.sentence(),
                created_at=fake.date_time_between(start_date='-1y', end_date='now'),
                model_id=random.randint(1, 5)
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
    # Generate approximately 30 messages per conversation
    for conversation in conversations:
        # Generate between 20-40 messages per conversation
        message_count = 10
        
        # Get user associated with this conversation
        user = db.query(User).filter(User.external_id == conversation.user_id).first()
        if not user:
            continue
            
        # Generate a sequence of messages for this conversation
        for i in range(message_count):
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
                
                # Alternate between user and bot messages
                is_bot = (i % 2 == 1)
                
                # Calculate a timestamp that increases with each message
                msg_time_delta = timedelta(minutes=random.randint(1, 15) * i)
                msg_timestamp = conversation.created_at + msg_time_delta
                
                message = Message(
                    external_id=3000 + inserted_count,
                    conversation_id=conversation.external_id,
                    message=fake.paragraph(),
                    is_bot=is_bot,
                    sender_id=user.external_id,
                    chat_parameter=chat_params,
                    created_at=msg_timestamp
                )
                db.add(message)
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
        # generate_role_types(db)
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
    print("Fake data generation completed.")