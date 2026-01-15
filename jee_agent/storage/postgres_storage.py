from typing import Optional, Dict, Any
import json
from sqlalchemy import create_engine, text
from jee_agent.config.settings import DATABASE_URL

class StudentStorage:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self._init_db()

    def _init_db(self):
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    data JSONB
                )
            """))
            conn.commit()

    def get(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT data FROM students WHERE student_id = :id"),
                {"id": student_id}
            ).fetchone()
            if result:
                # result[0] is the JSONB data, automatically converted to dict by SQLAlchemy/psycopg
                return result[0]
            return None

    def upsert(self, student_id: str, data: Dict[str, Any]):
        with self.engine.connect() as conn:
            # SQLAlchemy 2.0+ with psycopg should handle JSONB automatically
            conn.execute(
                text("""
                    INSERT INTO students (student_id, data) 
                    VALUES (:id, :data)
                    ON CONFLICT (student_id) 
                    DO UPDATE SET data = :data
                """),
                {"id": student_id, "data": json.dumps(data)} 
            )
            conn.commit()

    def clear(self):
        """Clear all student data"""
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE students"))
            conn.commit()
