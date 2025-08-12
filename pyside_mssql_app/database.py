import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# IMPORTANT: Replace with your actual MS SQL Server connection details
# The format is: "mssql+pyodbc://<username>:<password>@<server_name>/<database_name>?driver=ODBC+Driver+17+for+SQL+Server"
# Ensure you have the 'ODBC Driver 17 for SQL Server' installed.
DATABASE_URL = "mssql+pyodbc://user:password@localhost/mydatabase?driver=ODBC+Driver+17+for+SQL+Server"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class PN(Base):
        __tablename__ = "PN"

        id = Column(Integer, primary_key=True, index=True)
        partnumber = Column(String(50), unique=True, index=True, nullable=False)
        note = Column(String(255))

        pins = relationship("Pin", back_populates="pn", cascade="all, delete-orphan")

    class Pin(Base):
        __tablename__ = "pin"

        id = Column(Integer, primary_key=True, index=True)
        pn_id = Column(Integer, ForeignKey("PN.id"), nullable=False)
        pin = Column(String(50), nullable=False)
        name = Column(String(50))
        base_pin = Column(String(50))
        note = Column(String(255))

        pn = relationship("PN", back_populates="pins")

except ImportError:
    # This is a fallback message for the main application if dependencies are missing.
    print("SQLAlchemy or pyodbc is not installed. Please run: pip install SQLAlchemy pyodbc")
except Exception as e:
    # This will catch connection errors when the application starts.
    print(f"An error occurred during database initialization: {e}")
    # The main application will handle showing this error to the user.
    raise
