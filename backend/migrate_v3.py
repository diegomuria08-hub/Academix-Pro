import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.db.database import engine

def migrate():
    print("Running migration v3 for Liceo Lapsos support...")
    with engine.connect() as conn:
        ins = inspect(engine)
        
        # 1. Update evaluations: add lapso_number
        eval_cols = [c['name'] for c in ins.get_columns('evaluations')]
        if 'lapso_number' not in eval_cols:
            conn.execute(text("ALTER TABLE evaluations ADD COLUMN lapso_number INT NOT NULL DEFAULT 1"))
            print("Added lapso_number to evaluations")
        else:
            print("lapso_number already exists in evaluations")
            
        # 2. Update academic_settings: add total_lapsos and current_lapso
        set_cols = [c['name'] for c in ins.get_columns('academic_settings')]
        if 'total_lapsos' not in set_cols:
            conn.execute(text("ALTER TABLE academic_settings ADD COLUMN total_lapsos INT NOT NULL DEFAULT 3"))
            print("Added total_lapsos to academic_settings")
        else:
            print("total_lapsos already exists in academic_settings")

        if 'current_lapso' not in set_cols:
            conn.execute(text("ALTER TABLE academic_settings ADD COLUMN current_lapso INT NOT NULL DEFAULT 1"))
            print("Added current_lapso to academic_settings")
        else:
            print("current_lapso already exists in academic_settings")

        conn.commit()
    print("Migration v3 completed successfully!")

if __name__ == "__main__":
    migrate()
