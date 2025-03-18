from datetime import datetime, timezone
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import Conversation, User

def update_display_flag():
    db = SessionLocal()
    try:
        # Get conversations created from March 10, 2025 00:00:00 UTC
        start_date = datetime(2025, 3, 10, tzinfo=timezone.utc)
        # Only join the User table since that's all we need
        conversations = (
            db.query(Conversation)
            .join(User, Conversation.user_id == User.external_id)
            .filter(Conversation.created_at >= start_date)
            .all()
        )
        
        for conv in conversations:
            user = conv.user
            # For external users (internal_user_flag = False)
            if not user.internal_user_flag:
                # External users should not have personnel and display_flag should be False
                if user.personnel:
                    raise Exception(f"External user {user.username} should not have personnel record")
                conv.display_flag = False
            else:
                # For internal users, they must have personnel
                if not user.personnel:
                    raise Exception(f"Internal user {user.username} must have personnel record")
                conv.display_flag = True
        
        # Commit the changes
        db.commit()
        print("Successfully updated display_flag for conversations")
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_display_flag()
