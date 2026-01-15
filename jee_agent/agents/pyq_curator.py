from textwrap import dedent
from typing import List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from jee_agent.knowledge.pyq_loader import PYQKnowledge
from jee_agent.config.settings import PRIMARY_MODEL


class PYQResponse(BaseModel):
    """Structured PYQ question response"""
    question_id: str = Field(description="Unique question identifier")
    question_text: str = Field(description="The question text")
    options: List[str] = Field(description="Answer options A, B, C, D")
    difficulty: str = Field(description="easy, medium, or hard")
    topic: str = Field(description="Topic being tested")
    estimated_time_mins: int = Field(description="Expected time to solve in minutes")
    hint: Optional[str] = Field(default=None, description="Optional hint if student is stuck")
    motivation: str = Field(description="Encouraging message for the student")


class PYQFeedback(BaseModel):
    """Structured feedback after student attempts"""
    is_correct: bool = Field(description="Whether the answer was correct")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Clear explanation of the solution")
    common_mistakes: List[str] = Field(description="Common mistakes students make")
    similar_patterns: List[str] = Field(description="Similar question patterns to practice")
    time_analysis: str = Field(description="Analysis of time taken vs expected")
    next_difficulty: str = Field(description="Recommended next difficulty level")


def create_pyq_curator_agent(knowledge: PYQKnowledge) -> Agent:
    return Agent(
        name="PYQ Curator",
        model=OpenAIChat(id=PRIMARY_MODEL),
        knowledge=knowledge.knowledge_base,
        search_knowledge=True,
        description="Curates and serves relevant PYQs based on student's current level",
        # Use structured output for type-safe responses
        output_schema=PYQResponse,
        instructions=dedent("""
            You are a JEE PYQ specialist. Your job is to serve the RIGHT question 
            at the RIGHT time.
            
            CURATION RULES:
            1. Start each topic with an EASY confidence builder
            2. Progress: Easy (2) → Medium (2) → Hard (1)
            3. Prioritize questions from 2020-2025 (most relevant patterns)
            4. Tag each question with: concept tested, common mistakes, time estimate
            
            WHEN SERVING A QUESTION:
            - Present clearly formatted question with options
            - Do NOT show answer until student attempts
            - After attempt, provide:
              * Correct answer with fastest solution method
              * Why wrong options are traps
              * Similar pattern questions to try next
            
            PATTERN RECOGNITION:
            - After every 5 questions, summarize the pattern
            - Tell student: "80% of [topic] questions test [concept]"
            - Identify if student is repeatedly failing same pattern
            
            NEVER:
            - Dump multiple questions at once
            - Give answer before student tries
            - Repeat exact same question in a session
        """),
        markdown=True
    )

PYQCuratorAgent = create_pyq_curator_agent