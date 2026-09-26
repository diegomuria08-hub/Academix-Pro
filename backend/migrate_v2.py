import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.db.database import engine

def migrate():
    with engine.connect() as conn:
        ins = inspect(engine)
        
        # 1. Update subjects
        sub_cols = [c['name'] for c in ins.get_columns('subjects')]
        if 'code' not in sub_cols:
            conn.execute(text("ALTER TABLE subjects ADD COLUMN code VARCHAR(50) NULL"))
            print("Added code to subjects")
        if 'target_grade' not in sub_cols:
            conn.execute(text("ALTER TABLE subjects ADD COLUMN target_grade FLOAT NULL DEFAULT 20.0"))
            print("Added target_grade to subjects")
            
        # 2. Update evaluations
        eval_cols = [c['name'] for c in ins.get_columns('evaluations')]
        if 'description' not in eval_cols:
            conn.execute(text("ALTER TABLE evaluations ADD COLUMN description TEXT NULL"))
            print("Added description to evaluations")
        if 'status' not in eval_cols:
            conn.execute(text("ALTER TABLE evaluations ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pendiente'"))
            print("Added status to evaluations")
        if 'max_grade' not in eval_cols:
            conn.execute(text("ALTER TABLE evaluations ADD COLUMN max_grade FLOAT NOT NULL DEFAULT 20.0"))
            print("Added max_grade to evaluations")

        # 3. Update academic_settings
        set_cols = [c['name'] for c in ins.get_columns('academic_settings')]
        if 'evaluation_mode' not in set_cols:
            conn.execute(text("ALTER TABLE academic_settings ADD COLUMN evaluation_mode VARCHAR(30) NOT NULL DEFAULT 'university'"))
            print("Added evaluation_mode to academic_settings")
        if 'default_eval_count' not in set_cols:
            conn.execute(text("ALTER TABLE academic_settings ADD COLUMN default_eval_count INT NOT NULL DEFAULT 5"))
            print("Added default_eval_count to academic_settings")

        # 4. Create class_schedules table
        if 'class_schedules' not in ins.get_table_names():
            conn.execute(text("""
                CREATE TABLE class_schedules (
                    id VARCHAR(36) PRIMARY KEY,
                    subject_id VARCHAR(36) NOT NULL,
                    day_of_week INT NOT NULL,
                    start_time VARCHAR(10) NOT NULL,
                    end_time VARCHAR(10) NOT NULL,
                    classroom VARCHAR(100) NULL,
                    professor VARCHAR(100) NULL,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            """))
            print("Created table class_schedules")

        # 5. Create academic_events table
        if 'academic_events' not in ins.get_table_names():
            conn.execute(text("""
                CREATE TABLE academic_events (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    subject_id VARCHAR(36) NULL,
                    evaluation_id VARCHAR(36) NULL,
                    title VARCHAR(150) NOT NULL,
                    description TEXT NULL,
                    event_date DATETIME NOT NULL,
                    reminder_lead_time_hours INT NOT NULL DEFAULT 24,
                    is_notified BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE SET NULL
                )
            """))
            print("Created table academic_events")
            
        conn.commit()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
