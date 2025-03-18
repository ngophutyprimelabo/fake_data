from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = (
    f"mysql+pymysql://dev:dev@localhost:3306/fake_db"
)

# Add connection pool and timeout settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4", "connect_timeout": 60},
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Thay vì kết nối ngay lập tức, nên thực hiện khi cần
engine.connect()

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
