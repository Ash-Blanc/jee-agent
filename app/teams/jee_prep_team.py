from textwrap import dedent
from uuid import uuid4
from agno.team import Team
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from agents import (
    DailyPlannerAgent,
    PYQCuratorAgent,
    TheoryCoachAgent,
    LectureOptimizerAgent,
    StressMonitorAgent,
    MemoryCuratorAgent
)
from knowledge.pyq_loader import PYQKnowledge
from config.settings import DB_PATH, PRIMARY_MODEL

def create_jee_prep_team(student_id: str, session_id: str | None = None) -> Team:
    """
    Creates the full JEE prep team with proper Agno best practices.
    
    Args:
        student_id: Unique identifier for the student
        session_id: Optional session ID for continuing conversations
        
    Returns:
        Configured Team instance with all agents and memory
    """
    
    # Use SqliteDb for proper session and memory management
    db = SqliteDb(
        table_name="jee_prep_sessions",
        db_file=DB_PATH
    )
    
    # Initialize knowledge base
    pyq_knowledge = PYQKnowledge()
    
    # Create all agents with proper configuration
    daily_planner = DailyPlannerAgent()
    pyq_curator = PYQCuratorAgent(pyq_knowledge)
    theory_coach = TheoryCoachAgent()
    lecture_optimizer = LectureOptimizerAgent()
    stress_monitor = StressMonitorAgent()
    memory_curator = MemoryCuratorAgent()
    
    # Create coordinated team with Agno best practices
    team = Team(
        name="JEE Adaptive Learning System",
        model=OpenAIChat(id=PRIMARY_MODEL),
        members=[
            daily_planner,
            pyq_curator,
            theory_coach,
            lecture_optimizer,
            stress_monitor,
            memory_curator
        ],
        # Database for session persistence
        db=db,
        # Enable user memories for personalization
        enable_user_memories=True,
        # Enable agentic memory for intelligent memory management
        enable_agentic_memory=True,
        # Session configuration
        session_id=session_id or str(uuid4()),
        user_id=student_id,
        instructions=dedent("""
            COORDINATION PROTOCOL FOR JEE PREP:
            
            === SESSION START ===
            1. Memory curator loads student state
            2. Daily planner generates/updates today's schedule
            3. Present plan to student, confirm availability
            
            === DURING SESSION ===
            4. Lecture optimizer queues content if needed
            5. PYQ curator serves questions adaptively
            6. Theory coach activates ONLY when student stuck >2 mins
            7. Stress monitor runs continuously (background)
            8. Memory curator logs all interactions
            
            === TOPIC FLOW ===
            For each topic:
            - Start with 1 EASY PYQ (confidence builder)
            - If solved correctly → next harder PYQ
            - If stuck >2 mins → Theory coach micro-injection
            - After 5 PYQs → Pattern summary
            - Every 30 mins → Stress check
            
            === SESSION END ===
            9. Memory curator commits all learnings
            10. Daily planner adjusts tomorrow's plan
            11. End on a WIN (always finish with solved question)
            
            === HANDOFF RULES ===
            - PYQ Curator → Theory Coach: When student stuck
            - Theory Coach → PYQ Curator: After explanation, return to practice
            - Any Agent → Stress Monitor: When stress signals detected
            - Stress Monitor → Daily Planner: When session should end
            
            === NEVER ===
            - Dump multiple questions at once
            - Give theory before student attempts
            - Mention time pressure negatively
            - Make student feel behind
        """),
        # Response configuration
        markdown=True,
        show_tool_calls=False,  # Keep UI clean
        show_members_responses=True,  # Show which agent is responding
        add_datetime_to_context=True,
        # Members respond directly without team leader synthesis
        respond_directly=False,  # Team leader coordinates responses
        # Performance optimization
        enable_session_summaries=False,  # Not needed for workflow sessions
    )
    
    return team