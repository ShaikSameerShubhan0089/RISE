import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine('mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss')

def check():
    with engine.connect() as conn:
        tables = ['districts', 'mandals', 'anganwadi_centers', 'users', 'children', 'assessments']
        for t in tables:
            print(f"--- Table: {t} ---")
            # Get the primary key column name
            res = conn.execute(text(f"SHOW KEYS FROM {t} WHERE Key_name = 'PRIMARY'")).fetchone()
            if not res:
                print("No primary key found.")
                continue
            pk = res[4] # Column_name
            print(f"Primary Key: {pk}")
            
            # Check for duplicates
            query = text(f"SELECT {pk}, COUNT(*) FROM {t} GROUP BY {pk} HAVING COUNT(*) > 1")
            dupes = conn.execute(query).fetchall()
            if dupes:
                print(f"!!! FOUND {len(dupes)} DUPLICATES in {t}")
                print(dupes[:5])
            else:
                print(f"✓ {t} has no duplicate primary keys.")

if __name__ == "__main__":
    check()
