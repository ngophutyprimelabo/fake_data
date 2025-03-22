from faker import Faker
from sqlalchemy.orm import Session
from core.database_prod import SessionLocal, engine
from model_prod import User, ChatModel, ChatConversation, ChatMessage, CategoryGroup, ChatParameter, ChatParameterGroup
import random
from datetime import datetime, timedelta

# Initialize faker
fake = Faker()

def create_users(db: Session, count: int = 50):
    """Create fake users"""
    users = []
    for _ in range(count):
        user = {
            "username": fake.user_name(),
            "password": "pbkdf2_sha256$600000$salt$hashedpassword",  # Example hashed password
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "is_staff": random.choice([True, False]),
            "is_active": True,
            "is_superuser": False,
            "date_joined": fake.date_time_between(start_date='-1y'),
            "last_login": fake.date_time_between(start_date='-1m')
        }
        users.append(user)
    return users

def create_chat_models(db: Session, count: int = 5):
    """Create fake chat models"""
    models = []
    for i in range(count):
        model = {
            "name": f"Model {i+1}",
            "order": i,
            "is_eval": random.choice([True, False]),
            "is_return_markdown": random.choice([True, False]),
            "text_explain": fake.text(max_nb_chars=200),
            "is_single_conversation": random.choice([True, False]),
            "is_summary_menu": random.choice([True, False]),
            "is_premise_statement": random.choice([True, False]),
            "premise_statement": fake.text(max_nb_chars=100),
            "premise_statement_response": fake.text(max_nb_chars=100),
            "output_screen_type": random.choice(["standard", "split", "full"])
        }
        models.append(model)
    return models

def create_chat_conversations(db: Session, count: int = 50):
    """Create fake chat conversations"""
    conversations = []
    for _ in range(count):
        conversation = {
            "user_id": random.randint(1, 50),  # Assuming 50 users
            "topic": fake.sentence(nb_words=4),
            "created_at": fake.date_time_between(start_date='-1y'),
            "model_id": random.randint(1, 5),  # Assuming 5 models
            "is_delete": False,
            "file_upload_type": random.randint(0, 2),
            "thread_id": fake.uuid4() if random.choice([True, False]) else None,
            "vector_store_id": fake.uuid4() if random.choice([True, False]) else None
        }
        conversations.append(conversation)
    return conversations

def create_chat_messages(db: Session, count: int = 100):
    """Create fake chat messages"""
    messages = []
    for _ in range(count):
        message = {
            "conversation_id": random.randint(1, 50),  # Assuming 50 conversations
            "message": fake.text(max_nb_chars=200),
            "is_bot": random.choice([True, False]),
            "created_at": fake.date_time_between(start_date='-1y'),
            "chat_parameter": {"param1": fake.word(), "param2": fake.word()},
            "bad_reason": "" if random.random() > 0.2 else fake.text(max_nb_chars=50),
            "is_bad": False,
            "is_good": random.choice([True, False]),
            "corrected_document_name": fake.file_name(),
            "corrected_document_page": str(random.randint(1, 100)),
            "corrected_document_title": fake.sentence(nb_words=3)
        }
        messages.append(message)
    return messages

def main():
    db = SessionLocal()
    try:
        users = create_users(db)
        chat_models = create_chat_models(db)
        conversations = create_chat_conversations(db)
        messages = create_chat_messages(db)

        db.bulk_insert_mappings(User, users)
        db.bulk_insert_mappings(ChatModel, chat_models)
        db.bulk_insert_mappings(ChatConversation, conversations)
        db.bulk_insert_mappings(ChatMessage, messages)
        
        db.commit()
        print("Fake data generated successfully!")
        
    except Exception as e:
        print(f"Error generating fake data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()