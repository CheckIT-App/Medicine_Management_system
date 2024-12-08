from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

 
# Replace with your actual database connection details
DATABASE_URL = "postgresql://postgres:manage1234@localhost/medicine_management"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for defining models
Base = declarative_base()

# Dependency for creating and closing a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
