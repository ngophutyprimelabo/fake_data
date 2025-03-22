from typing import List, Any, Type, TypeVar
from sqlalchemy.orm import Session
from core.database import get_db as get_db_local
from core.database_prod import get_db
from sqlalchemy.ext.declarative import DeclarativeMeta
from model_prod import *
from models import *

Base = TypeVar('Base', bound=DeclarativeMeta)
taget_db = next(get_db_local())

def batch_get_data(
    db_model: Type[Base],
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: dict = None
) -> List[Any]:
    query = db.query(db_model)
    
    if filters:
        for key, value in filters.items():
            if hasattr(db_model, key):
                query = query.filter(getattr(db_model, key) == value)
    
    return query.offset(skip).limit(limit).all()

def get_all_data(
    db_model: Type[Base],
    db: Session,
    filters: dict = None
) -> List[Any]:
    query = db.query(db_model)
    
    if filters:
        for key, value in filters.items():
            if hasattr(db_model, key):
                query = query.filter(getattr(db_model, key) == value)
    
    return query.all()

def get_table_data(model: Type[Base], skip: int = 0, limit: int = 100, filters: dict = None) -> List[Any]:
    db = next(get_db())
    try:
        return batch_get_data(model, db, skip, limit, filters)
    finally:
        db.close()

def get_all_table_data(model: Type[Base], filters: dict = None) -> List[Any]:
    db = next(get_db())
    try:
        return get_all_data(model, db, filters)
    finally:
        db.close()

# data = get_table_data(ChatMessage, filters={"is_eval": True})
chat_message = get_all_table_data(ChatMessage)
i=0
for chat in chat_message:
    i+=1
    d = User(
            external_id=chat.id,
            external_id_delete_flag=0,
            username="hello" +f'{i}',
            internal_user_flag=True,
            created_at=datetime.now(),
    )

    taget_db.add(d)
    taget_db.commit()
taget_db.close()