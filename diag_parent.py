import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv('backend/.env')
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # 1. Check parent users
    print("=== Parent Users (first 5) ===")
    parents = conn.execute(text(
        "SELECT user_id, email, full_name FROM users WHERE role = 'parent' LIMIT 5"
    ))
    parent_rows = list(parents)
    for r in parent_rows:
        print(f"  user_id={r[0]}, email={r[1]}, name={r[2]}")
    
    if parent_rows:
        test_uid = parent_rows[0][0]
        print(f"\n=== Mappings for user_id={test_uid} ===")
        mappings = conn.execute(text(
            f"SELECT * FROM parent_child_mapping WHERE user_id = {test_uid}"
        ))
        mapping_rows = list(mappings)
        if mapping_rows:
            for r in mapping_rows:
                print(f"  {dict(r._mapping)}")
        else:
            print("  ** NO MAPPINGS FOUND **")
        
        # 2. Total mapping count
        total = conn.execute(text("SELECT COUNT(*) FROM parent_child_mapping")).scalar()
        print(f"\n=== Total parent_child_mapping rows: {total} ===")
        
        # 3. Check if ANY parent has mappings
        parents_with_map = conn.execute(text(
            "SELECT pcm.user_id, u.email, COUNT(pcm.child_id) as cnt "
            "FROM parent_child_mapping pcm "
            "JOIN users u ON pcm.user_id = u.user_id "
            "GROUP BY pcm.user_id, u.email "
            "ORDER BY cnt DESC LIMIT 5"
        ))
        print("\n=== Parents WITH mappings (top 5) ===")
        for r in parents_with_map:
            print(f"  user_id={r[0]}, email={r[1]}, children={r[2]}")
    else:
        print("  NO parent users found!")
