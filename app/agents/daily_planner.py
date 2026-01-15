from textwrap import dedent
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config.settings import PRIMARY_MODEL, EXAM_DATE


class TimeBlock(BaseModel):
    """Structured time block for study plan"""
    start_time: str = Field(description="Start time in HH:MM format")
    end_time: str = Field(description="End time in HH:MM format")
    subject: str = Field(description="Subject to study")
    topics: List[str] = Field(description="Specific topics to cover")
    target_pyqs: int = Field(description="Number of PYQs to attempt")
    activity_type: str = Field(description="lecture, practice, revision, or break")
    notes: str = Field(default="", description="Additional notes or tips")


class DailyPlan(BaseModel):
    """Structured daily study plan output"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    total_hours: float = Field(description="Total study hours planned")
    focus_subject: str = Field(description="Primary subject focus for the day")
    time_blocks: List[TimeBlock] = Field(description="Scheduled time blocks")
    motivation_message: str = Field(description="Personalized motivation for the day")
    key_goals: List[str] = Field(description="Top 3 goals for the day")


def create_daily_planner_agent() -> Agent:
    return Agent(
        name="Daily Planner",
        model=OpenAIChat(id=PRIMARY_MODEL),
        description="Creates and adapts daily study plans based on student progress",
        # Use structured output for type-safe responses
        output_schema=DailyPlan,
        instructions=dedent(f"""
            You are an adaptive JEE Main study planner. Exam date: {EXAM_DATE}
            
            YOUR RESPONSIBILITIES:
            1. Generate personalized daily study schedules
            2. Adjust plans based on yesterday's performance
            3. Prioritize topics by: weakness + exam weightage + time remaining
            4. Balance subjects to prevent burnout
            
            SCHEDULING RULES:
            - Morning blocks (high energy): Tackle weakest high-weightage topics
            - Afternoon blocks: Medium difficulty, mixed practice
            - Evening blocks (low energy): Revision + confidence builders
            - Never schedule >3 hours without a break
            - Always end day on a WIN (solved question)
            
            ADAPTATION LOGIC:
            - If yesterday's accuracy <40%: Reduce difficulty, add more basics
            - If accuracy >70%: Increase challenge, move faster
            - If topic taking too long: Flag for review, consider skipping
            
            OUTPUT FORMAT:
            Return a structured DailyPlan with:
            - Time blocks with specific topics
            - Target PYQ count per block
            - Activity types (lecture/practice/revision/break)
            - Personalized motivation message
            - Top 3 goals for the day
        """),
        markdown=True,
        add_datetime_to_context=True
    )

DailyPlannerAgent = create_daily_planner_agent