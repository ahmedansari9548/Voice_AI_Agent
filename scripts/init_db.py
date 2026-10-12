from sqlalchemy import inspect

from app.db.database import Base, engine, test_connection
from app.models.patient import Patient

print("Connecting to PostgreSQL...")
print("Database:", test_connection())

print("Creating database tables...")
Base.metadata.create_all(bind=engine)

inspector = inspect(engine)

print("\nAvailable tables:")
for table in inspector.get_table_names():
    print(" -", table)

print("\nPatient table columns:")
for column in inspector.get_columns("patients"):
    print(
        f" - {column['name']}: "
        f"{column['type']}"
    )

print("\nDatabase initialized successfully!")
