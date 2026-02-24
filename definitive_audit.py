import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')
pg = create_engine(os.getenv('DATABASE_URL'))
ms = create_engine('mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss')

tables = [
    'states', 'districts', 'mandals', 'anganwadi_centers', 'users', 
    'children', 'assessments', 'engineered_features', 'model_predictions', 
    'referrals', 'interventions', 'audit_logs', 'parent_child_mapping', 
    'district_summary'
]

print("| Table | MySQL | Postgres | Match |")
print("|---|---|---|---|")
for t in tables:
    try:
        with ms.connect() as c1, pg.connect() as c2:
            count1 = c1.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            count2 = c2.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            match = "YES" if count1 == count2 else "NO"
            print(f"| {t} | {count1} | {count2} | {match} |")
    except Exception as e:
        print(f"| {t} | Error | Error | N/A |")
