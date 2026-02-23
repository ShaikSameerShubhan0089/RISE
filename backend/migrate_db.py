from sqlalchemy import text
from database import engine

def migrate():
    print("Checking for missing columns...")
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SHOW COLUMNS FROM children LIKE 'caregiver_additional_info'"))
            if not result.fetchone():
                print("Adding 'caregiver_additional_info' to 'children' table...")
                conn.execute(text("ALTER TABLE children ADD COLUMN caregiver_additional_info TEXT AFTER caregiver_email"))
                conn.commit()
                print("✓ Migration successful")
            else:
                print("✓ Column already exists")
        except Exception as e:
            print(f"✗ Migration failed: {e}")

if __name__ == "__main__":
    migrate()
