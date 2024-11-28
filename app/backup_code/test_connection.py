from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse

# Direct database connection parameters
server = "34.30.185.244"  # IP address of the database server
database = "scvacs"       # Your database name
username = "sqlserver"    # Database username
password = urllib.parse.quote_plus("scvacs@1234")  # Escape special characters in password
port = "1433"  # Default SQL Server port

# SQLAlchemy connection string using pytds
DATABASE_URL = (
    f"mssql+pytds://{username}:{password}@{server}:{port}/{database}"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)  # Echo=True for detailed logs
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def test_connection():
    """Test connection to GCP SQL Server."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * from vehicle_history"))
            for row in result:
                print(f"Database connected successfully! Test query result: {row[0]}")
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_connection()
