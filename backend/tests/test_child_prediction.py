import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

import unittest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Base, engine
import models
import schemas

class TestChildrenManagement(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        # No automated DB setup/teardown here to avoid messing up dev DB
        # This is a manual-run verification script

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_schema_changes(self):
        # Verify the schema has caregiver_additional_info
        print("Checking Child schemas...")
        fields = getattr(schemas.ChildBase, 'model_fields', getattr(schemas.ChildBase, '__fields__', {}))
        self.assertIn('caregiver_additional_info', fields)
        print("✓ ChildBase schema updated")
        
        # Verify the model has caregiver_additional_info
        print("Checking Child model...")
        import sqlalchemy
        inspector = sqlalchemy.inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('children')]
        print(f"Columns in children table: {columns}")
        self.assertIn('caregiver_additional_info', columns)
        print("✓ Child model updated in DB")

    def test_prediction_router_logic(self):
        # Verify ModelType enum
        self.assertIn('Model A', [m.value for m in schemas.ModelType])
        self.assertIn('Model B', [m.value for m in schemas.ModelType])
        print("✓ ModelType enum updated")

if __name__ == "__main__":
    unittest.main()
