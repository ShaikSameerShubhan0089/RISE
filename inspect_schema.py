import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
url = os.getenv("DATABASE_URL")
engine = create_engine(url)
inspector = inspect(engine)
columns = inspector.get_columns('assessments')
print(f"{'Column':<35} | {'Type'}")
print("-" * 50)
for col in columns:
    print(f"{col['name']:<35} | {col['type']}")
