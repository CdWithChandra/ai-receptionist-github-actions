from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create (or use) a SQLite database named ai_receptionist.db in the current directory.
DATABASE_URL= "sqlite:///./ai_receptionist.db" 

# The engine is SQLAlchemy's connection manager. Every database operation will go through this engine.
engine = create_engine(
    DATABASE_URL,
    echo=True, # This tells SQLAlchemy to print every SQL statement to the terminal for debugging. 
)

# Whenever we need to talk to the database, we'll create a session like this:
SessionLocal= sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
        """
    Create a database session for each request.

    Yields:
        Session: SQLAlchemy database session.
    """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
        