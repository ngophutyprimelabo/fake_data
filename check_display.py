from sqlalchemy.orm import Session
from connect import SessionLocal
from models import Conversation, User

def update_display_flag():
    db = SessionLocal()
    try:
        # Get all conversations with their users
        conversations = db.query(Conversation).join(Conversation.user).all()
        
        for conv in conversations:
            # Check if user has no personnel record
            if not conv.user.personnel:
                # Update display_flag to 1
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
