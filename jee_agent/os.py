from agno.os import AgentOS

from jee_agent.agents import (
    DailyPlannerAgent,
    PYQCuratorAgent,
    TheoryCoachAgent,
    LectureOptimizerAgent,
    StressMonitorAgent,
    MemoryCuratorAgent
)
from jee_agent.teams.jee_prep_team import create_jee_prep_team
from jee_agent.storage.database import agent_db, StudentStorage

# 1. Initialize Student Storage (App logic DB)
# This ensures the DB structure exists.
student_storage = StudentStorage()

# 2. Create the Team using the shared storage
# Using a placeholder ID for the OS view. In a real deployment,
# the UI/Client would likely specify user_id in the request.
jee_team = create_jee_prep_team(
    student_id="os-default-user", 
    db=agent_db
)

# 3. Initialize AgentOS
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

app = agent_os.get_app()

if __name__ == "__main__":
    # Default port is 7777; change with port=...
    agent_os.serve(app="__main__:app", reload=True)