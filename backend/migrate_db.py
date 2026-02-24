from sqlalchemy import text
from database import engine

def migrate():
    print("Checking for missing columns...")
    with engine.connect() as conn:
        try:
            # Check if column exists (PostgreSQL compatible)
            query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='children' AND column_name='caregiver_additional_info'
            """)
            result = conn.execute(query)
            
            if not result.fetchone():
                print("Adding 'caregiver_additional_info' to 'children' table...")
                # PostgreSQL doesn't support 'AFTER' clause
                conn.execute(text("ALTER TABLE children ADD COLUMN caregiver_additional_info TEXT"))
                conn.commit()
                print("✓ Migration successful")
            else:
                print("✓ Column already exists")
        except Exception as e:
            print(f"✗ Migration failed: {e}")

if __name__ == "__main__":
    migrate()
