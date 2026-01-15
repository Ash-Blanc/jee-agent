from agno.os import AgentOS
from agno.db.postgres import PostgresDb
from agno.db.sqlite import SqliteDb

from jee_agent.agents import (
    DailyPlannerAgent,
    PYQCuratorAgent,
    TheoryCoachAgent,
    LectureOptimizerAgent,
    StressMonitorAgent,
    MemoryCuratorAgent
)
from jee_agent.teams.jee_prep_team import create_jee_prep_team
from jee_agent.storage.db import StudentStorage
from jee_agent.config.settings import DATABASE_URL

# 1. Initialize Student Storage (App logic DB)
# This ensures the DB structure exists.
student_storage = StudentStorage()

# 2. Configure AgentOS Storage (Agno Sessions DB)
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    agent_storage = SqliteDb(
        table_name="jee_prep_sessions",
        db_file=db_path
    )
else:
    agent_storage = PostgresDb(
        session_table="jee_prep_sessions",
        db_url=DATABASE_URL
    )

# 3. Create the Team using the shared storage
# Using a placeholder ID for the OS view. In a real deployment,
# the UI/Client would likely specify user_id in the request.
jee_team = create_jee_prep_team(
    student_id="os-default-user", 
    db=agent_storage
)

# 4. Initialize AgentOS
agent_os = AgentOS(
    name="JEE Prep AI OS",
    description="Adaptive JEE Main preparation system",
    agents=[
        DailyPlannerAgent,
        PYQCuratorAgent,
        TheoryCoachAgent,
        LectureOptimizerAgent,
        StressMonitorAgent,
        MemoryCuratorAgent
    ],
    teams=[jee_team],
    # Configure tracing/storage if needed
    # tracing_db=agent_storage, # Optional: if tracing is enabled
)