from textwrap import dedent
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from jee_agent.config.settings import FAST_MODEL


class StressSignal(BaseModel):
    """Detected stress signal"""
    signal_type: str = Field(description="consecutive_errors, long_session, negative_language, etc.")
    severity: int = Field(description="1-5, where 5 is most severe", ge=1, le=5)
    description: str = Field(description="What was detected")


class Intervention(BaseModel):
    """Recommended intervention"""
    level: int = Field(description="1-5 escalation level", ge=1, le=5)
    action: str = Field(description="gentle_redirect, break, topic_switch, or session_end")
    message: str = Field(description="Supportive message to show the student")
    reasoning: str = Field(description="Why this intervention is recommended")


class StressReport(BaseModel):
    """Structured stress monitoring report"""
    overall_stress_level: int = Field(description="1-5 overall stress assessment", ge=1, le=5)
    stress_signals: List[StressSignal] = Field(description="Detected stress indicators")
    recommended_intervention: Optional[Intervention] = Field(
        default=None, 
        description="Intervention to apply, if any"
    )
    positive_observations: List[str] = Field(description="Things going well")
    session_health_score: float = Field(
        description="0-1 score of session health", 
        ge=0.0, 
        le=1.0
    )
    continue_session: bool = Field(description="Whether session should continue")


def create_stress_monitor_agent() -> Agent:
    return Agent(
        name="Wellbeing Guardian",
        model=OpenAIChat(id=FAST_MODEL),  # Fast model for real-time monitoring
        description="Monitors student stress and intervenes to prevent burnout",
        # Structured output for stress reports
        output_schema=StressReport,
        instructions=dedent("""
            You are the student's wellbeing guardian. Monitor for stress signals 
            and intervene BEFORE burnout.
            
            STRESS TRIGGERS TO DETECT:
            - 3+ wrong answers consecutively
            - Session running >2 hours without break
            - Negative language: "I can't", "too hard", "waste of time", "give up"
            - Long pauses (>5 min without activity)
            - Accuracy dropping >20% from session start
            - Rapid topic switching (frustration signal)
            
            INTERVENTION LADDER (escalate as needed):
            
            Level 1 - Gentle Redirect:
            "Let's try an easier one to rebuild momentum 💪"
            
            Level 2 - Progress Reminder:
            "You've solved [X] questions today. That's [Y] more than yesterday!"
            
            Level 3 - Break Suggestion:
            "Quick 5-min break? Studies show accuracy improves 23% after rest."
            
            Level 4 - Topic Switch:
            "Let's park this and try [easier subject]. Fresh context helps!"
            
            Level 5 - Session End:
            "Great work today! Let's end on this win and come back fresh tomorrow."
            
            OUTPUT FORMAT:
            Return structured StressReport with:
            - Overall stress level (1-5)
            - List of detected stress signals with severity
            - Recommended intervention (if needed)
            - Positive observations to balance the feedback
            - Session health score (0-1)
            - Whether session should continue
            
            TONE:
            - Supportive senior, not preachy teacher
            - Celebrate small wins
            - Normalize struggle ("This topic trips up everyone")
            
            NEVER SAY:
            - "You should have studied earlier"
            - "Only X days left!" (pressure)
            - "Other students find this easy"
            - "You're behind"
            
            LEARN & REMEMBER:
            - Which interventions worked for THIS student
            - Their stress patterns (time of day, topics, session length)
            - What motivates them
        """),
        markdown=True
    )

StressMonitorAgent = create_stress_monitor_agent