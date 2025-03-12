import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker
from connect import get_db, engine, Base
from models import (
    User, Personnel, Organization, Conversation, 
    Message, Tag, MessageTag, RoleType, EmployeeType,
    OrganizationType, FieldMapping, Abbreviation
)
from value import role_type, employee_type, field, field_detail, abbreviation

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
        
        # Insert Organization Types
        print("Generating organization types...")
        org_types = ["本社", "営業", "各支店", "その他"]
        for ot in org_types:
            if not db.query(OrganizationType).filter(OrganizationType.organization_type == ot).first():
                db.add(OrganizationType(organization_type=ot))
        db.commit()

        # Insert Field Mappings
        print("Generating field mappings...")
        for i in range(len(field)):
            if not db.query(FieldMapping).filter(FieldMapping.field_detail == field_detail[i]).first():
                db.add(FieldMapping(field=field[i], field_detail=field_detail[i]))
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
            org = Organization(
                external_department_code=fake.unique.bothify(text="?####"),
                external_division_code=fake.bothify(text="###"),
                external_section_code=fake.bothify(text="##"),
                field=random.choice(field),
                field_detail=random.choice(field_detail),
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
        for _ in range(300):
            personnel = Personnel(
                external_username=fake.unique.user_name(),
                entry_year=random.randint(1980, 2025),
                department_code=random.choice([org.external_department_code for org in organizations]),
                branch_code=fake.bothify(text="###"),
                head_office_name=fake.company(),
                branch_name=random.choice(abbreviation),
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
        personnel_usernames = [p.external_username for p in personnel_list]
        for username in personnel_usernames:
            user = User(
                external_id=1000 + len(users),
                external_id_delete_flag=random.choice([True, False]),
                username=username,  # Use personnel's external_username
                internal_user_flag=True,
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            users.append(user)
            db.add(user)
        
        # Create external users (500 - number of internal users)
        remaining = 500 - len(personnel_usernames)
        for i in range(remaining):
            user = User(
                external_id=1000 + len(users) + i,
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
            user = random.choice(users)
            conversation = Conversation(
                external_id=2000 + i,
                user_id=user.external_id,
                topic=f"対話 {i+1}: {fake.sentence()}",
                created_at=fake.date_time_between(start_date='-3m', end_date='now'),
                model_id=random.randint(1, 4),
                display_flag=not user.internal_user_flag
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
                    sender_id=conv.user_id,
                    chat_parameter=chat_params,
                    created_at=current_time
                ))
                
                # Bot response (5-30 seconds later)
                current_time += timedelta(seconds=random.randint(5, 30))
                db.add(Message(
                    external_id=fake.unique.random_number(digits=8),
                    conversation_id=conv.external_id,
                    message=fake.paragraph(),
                    is_bot=True,
                    sender_id=conv.user_id,
                    chat_parameter=chat_params,
                    created_at=current_time
                ))
                
                # Add delay before next pair
                current_time += timedelta(minutes=random.randint(1, 10))
        db.commit()

        # Generate Tags (100 records)
        print("Generating tags...")
        tags = []
        common_tags = [
            "技術", "ビジネス", "科学", "健康", "教育", "政治", "経済", "スポーツ",
            "エンターテイメント", "食品", "旅行", "ファッション", "テクノロジー", "自動車",
            "金融", "芸術", "音楽", "映画", "書籍", "ゲーム"
        ]
        for tag_name in common_tags:
            tag = Tag(
                name=tag_name,
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            tags.append(tag)
            db.add(tag)
        db.commit()

        # Generate Message Tags (1000 records)
        print("Generating message tags...")
        messages = db.query(Message).all()
        for _ in range(1000):
            db.add(MessageTag(
                message_id=random.choice(messages).external_id,
                tag_id=random.choice(tags).id,
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            ))
        db.commit()

        print("Data generation completed successfully!")

    except Exception as e:
        print(f"Error generating data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_data()
