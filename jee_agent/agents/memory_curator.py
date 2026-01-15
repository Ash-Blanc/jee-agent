from textwrap import dedent
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.tools.memory import MemoryTools

# Create a database connection for memory storage
memory_db = SqliteDb(db_file="data/student_memory.db")

class TopicUpdate(BaseModel):
    """Update for a specific topic's progress"""
    subject: str = Field(description="physics, chemistry, or math")
    topic: str = Field(description="Topic name")
    accuracy_change: float = Field(description="Change in accuracy percentage")
    time_spent_mins: int = Field(description="Time spent on this topic")
    confidence_level: str = Field(description="zero, low, medium, high, or mastered")
    notes: List[str] = Field(description="Key observations or breakthroughs")


class BehaviorObservation(BaseModel):
    """Behavioral pattern observation"""
    pattern_type: str = Field(description="energy, stress, preference, or learning_style")
    observation: str = Field(description="What was observed")
    actionable_insight: str = Field(description="How to use this insight")


class MemoryUpdate(BaseModel):
    """Structured memory update after interaction"""
    session_summary: str = Field(description="Brief summary of the session")
    topic_updates: List[TopicUpdate] = Field(description="Updates for topics practiced")
    behavior_observations: List[BehaviorObservation] = Field(description="Behavioral patterns")
    breakthroughs: List[str] = Field(description="Concepts that clicked for the student")
    struggles: List[str] = Field(description="Areas where student struggled")
    plan_adjustments: List[str] = Field(description="Recommended adjustments to study plan")
    next_session_focus: str = Field(description="What to focus on next session")


MemoryCuratorAgent = Agent(
        name="Learning Memory Curator",
        model="mistral:mistral-small-latest",
        description="Extracts and stores learnings from every interaction",
        # Use MemoryTools for intelligent memory management
        tools=[MemoryTools(db=memory_db, add_instructions=True)],
        # Structured output for memory updates
        output_schema=MemoryUpdate,
        instructions=dedent("""
            You are the memory curator. After EVERY interaction, extract 
            structured learnings to update the student state.
            
            EXTRACT AND STORE:
            
            1. PERFORMANCE SIGNALS:
               - Topic + accuracy on PYQs just attempted
               - Time taken vs expected time
               - Questions skipped or abandoned
               - Patterns in wrong answers
            
            2. PREFERENCE SIGNALS:
               - "This video was too fast" → reduce recommended speed
               - "I'm tired" → note energy dip time
               - "This concept clicked!" → mark as understood
               - Preferred explanation style
            
            3. BEHAVIORAL PATTERNS:
               - Session start/end times → infer peak hours
               - Topic switching frequency → boredom/frustration threshold
               - Accuracy trends → confidence trajectory
               - Break patterns → optimal session length
            
            4. BREAKTHROUGHS & STRUGGLES:
               - "Finally understood [concept]" → breakthrough
               - Repeated failures on same pattern → struggle point
               - Successful analogies/explanations → remember for future
            
            USE MEMORY TOOLS:
            - Use think() to analyze patterns before updating memory
            - Use add_memory() to store new insights about the student
            - Use update_memory() to refine existing observations
            - Use analyze() to determine if memory updates are complete
            
            OUTPUT FORMAT:
            Return structured MemoryUpdate with:
            - Session summary
            - Topic-specific updates with accuracy changes
            - Behavioral observations with actionable insights
            - Breakthroughs and struggles
            - Plan adjustments for next session
            
            RULES:
            - Update student_state object, don't just append logs
            - Prioritize actionable insights over raw data
            - Flag anomalies (sudden accuracy drop, unusual patterns)
        """),
        markdown=True
    )