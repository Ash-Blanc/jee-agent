from typing import Optional, Dict, Any
import json
import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, JSON, select
from sqlalchemy.dialects.postgresql import JSONB
from jee_agent.config.settings import DATABASE_URL

class StudentStorage:
    def __init__(self):
        # Ensure data directory exists for SQLite
        if DATABASE_URL.startswith("sqlite"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.engine = create_engine(DATABASE_URL)
        self.metadata = MetaData()
        
        # Define table using SQLAlchemy Core for dialect compatibility
        self.students = Table(
            "students",
            self.metadata,
            Column("student_id", String, primary_key=True),
            # Use JSON type which maps to JSON in SQLite and JSON in Postgres
            # For strict JSONB in Postgres, we'd need dialect specific logic, 
            # but generic JSON is fine for now.
            Column("data", JSON)
        )
        
        self._init_db()

    def _init_db(self):
        self.metadata.create_all(self.engine)

    def get(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self.engine.connect() as conn:
            stmt = select(self.students.c.data).where(self.students.c.student_id == student_id)
            result = conn.execute(stmt).fetchone()
            if result:
                # result[0] is the JSON data, automatically converted to dict
                return result[0]
            return None

    def upsert(self, student_id: str, data: Dict[str, Any]):
        with self.engine.connect() as conn:
            # Check if exists
            stmt = select(self.students.c.student_id).where(self.students.c.student_id == student_id)
            exists = conn.execute(stmt).fetchone()
            
            if exists:
                stmt = self.students.update().where(self.students.c.student_id == student_id).values(data=data)
            else:
                stmt = self.students.insert().values(student_id=student_id, data=data)
            
            conn.execute(stmt)
            conn.commit()

    def clear(self):
        """Clear all student data"""
        with self.engine.connect() as conn:
            conn.execute(self.students.delete())
            conn.commit()