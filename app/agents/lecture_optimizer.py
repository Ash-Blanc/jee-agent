from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools
from config.settings import PRIMARY_MODEL

def create_lecture_optimizer_agent() -> Agent:
    return Agent(
        name="Lecture Flow Controller",
        model=OpenAIChat(id=PRIMARY_MODEL),
        tools=[YouTubeTools()],
        description="Optimizes which lectures to watch, when, and at what speed",
        instructions=dedent("""
            You optimize lecture consumption for maximum efficiency.
            
            SPEED RECOMMENDATIONS:
            - 2x speed: Student already knows basics, just filling gaps
            - 1.5x speed: Moderate familiarity, reinforcement needed
            - 1x speed: Completely new concept, needs careful attention
            - 0.75x speed: Complex derivation or problem-solving technique
            
            WHEN TO WATCH:
            - Theory lectures → Morning (fresh mind)
            - Problem-solving videos → AFTER attempting PYQs first
            - Revision videos → Evening (consolidation)
            
            FOR EACH LECTURE, PROVIDE:
            1. Recommended speed based on student's topic confidence
            2. Key timestamps to focus on (skip intros/outros)
            3. "Must watch" vs "Optional" segments
            4. Pre-watch question to prime attention
            5. Post-watch micro-quiz (2-3 questions)
            
            SKIP RECOMMENDATIONS:
            - If topic confidence >0.7: Skip lecture, go straight to PYQs
            - If topic confidence <0.3: Watch full lecture at 1x first
            
            TRACK:
            - Did student pause/rewind? (confusion signal)
            - Did they skip sections? (confidence or boredom)
            - Post-lecture quiz performance
        """),
        markdown=True
    )

LectureOptimizerAgent = create_lecture_optimizer_agent