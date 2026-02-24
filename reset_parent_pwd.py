import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from sqlalchemy import create_engine, text
import bcrypt

engine = create_engine(os.getenv('DATABASE_URL'))

new_hash = bcrypt.hashpw("test123".encode(), bcrypt.gensalt()).decode()

with engine.connect() as conn:
    conn.execute(text(
        "UPDATE users SET password_hash = :hash WHERE email = 'parent_1@gmail.com'"
    ), {"hash": new_hash})
    conn.commit()
    print(f"Password reset for parent_1@gmail.com to 'test123'")
