from textwrap import dedent
from uuid import uuid4
from agno.team import Team
from agno.db.postgres import PostgresDb
from agno.models.openai import OpenAIChat

from jee_agent.agents import (
    DailyPlannerAgent,
    get_pyq_curator_agent,
    TheoryCoachAgent,
    LectureOptimizerAgent,
    StressMonitorAgent,
    MemoryCuratorAgent
)
from jee_agent.storage.database import agent_db
from jee_agent.config.settings import PRIMARY_MODEL, FALLBACK_MODEL, MISTRAL_API_KEY

def create_jee_prep_team(student_id: str, session_id: str | None = None, db: PostgresDb | None = None) -> Team:
    """
    Creates the full JEE prep team with proper Agno best practices.
    
    Args:
        student_id: Unique identifier for the student
        session_id: Optional session ID for continuing conversations
        db: Optional database instance for session storage (defaults to agent_db)
        
    Returns:
        Configured Team instance with all agents and memory
    """
    
    # Use centralized database if not provided
    if db is None:
        db = agent_db
    
    # Configure model using OpenAIChat compatible endpoint for Mistral
    # This bypasses potential serialization issues with LiteLLM/Groq integration
    model = OpenAIChat(
        id="mistral-large-latest",
        base_url="https://api.mistral.ai/v1",
        api_key=MISTRAL_API_KEY
    )
    
    # Instantiate PYQ Agent (this may trigger DB connection for vector store)
    pyq_agent = get_pyq_curator_agent()
    
    # Create coordinated team with Agno best practices
    team = Team(
        name="JEE Adaptive Learning System",
        model=model,
        members=[
            DailyPlannerAgent,
            pyq_agent,
            TheoryCoachAgent,
            LectureOptimizerAgent,
            StressMonitorAgent,
            MemoryCuratorAgent
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
        # show_tool_calls=False,  # Keep UI clean
        show_members_responses=True,  # Show which agent is responding
        add_datetime_to_context=True,
        # Members respond directly without team leader synthesis
        respond_directly=False,  # Team leader coordinates responses
        # Performance optimization
        enable_session_summaries=False,  # Not needed for workflow sessions
    )
    
    return team