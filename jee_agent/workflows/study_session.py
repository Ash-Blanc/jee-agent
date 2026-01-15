from typing import Optional
from agno.workflow import Workflow
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from jee_agent.agents import (
    DailyPlannerAgent,
    get_pyq_curator_agent,
    TheoryCoachAgent,
    StressMonitorAgent,
    MemoryCuratorAgent
)
from jee_agent.storage.student_state import StudentState
from jee_agent.config.settings import PRIMARY_MODEL

class StudySessionWorkflow:
    """
    Structured workflow for a single study session.
    More predictable than team coordination for core study loop.
    """
    
    def __init__(self, student_state: StudentState):
        self.student_state = student_state
        
        # Initialize agents
        self.planner = DailyPlannerAgent
        self.pyq_curator = get_pyq_curator_agent()
        self.theory_coach = TheoryCoachAgent
        self.stress_monitor = StressMonitorAgent
        self.memory_curator = MemoryCuratorAgent
    
    def create_topic_practice_workflow(self, topic: str, subject: str) -> Workflow:
        """Creates a workflow for practicing a single topic"""
        
        # Step 1: Get easy question
        easy_question_step = Agent(
            name="Easy Question Server",
            model=OpenAIChat(id=PRIMARY_MODEL),
            instructions=f"""
                Serve ONE easy {topic} question from the PYQ database.
                Format clearly with options A, B, C, D.
                Say: "Let's warm up with this one 🎯"
            """
        )
        
        # Step 2: Progress to medium
        medium_question_step = Agent(
            name="Medium Question Server", 
            model=OpenAIChat(id=PRIMARY_MODEL),
            instructions=f"""
                Student solved the easy question. Now serve a MEDIUM difficulty
                {topic} question. Say: "Nice! Ready for a bit more challenge?"
            """
        )
        
        # Step 3: Challenge with hard
        hard_question_step = Agent(
            name="Hard Question Server",
            model=OpenAIChat(id=PRIMARY_MODEL),
            instructions=f"""
                Student is doing well. Serve a HARD {topic} question.
                Say: "You're on fire! Let's try a tricky one 🔥"
            """
        )
        
        # Step 4: Pattern summary
        pattern_summary_step = Agent(
            name="Pattern Summarizer",
            model=OpenAIChat(id=PRIMARY_MODEL),
            instructions=f"""
                Summarize the patterns tested in {topic}:
                - Most common question types
                - Key formulas used
                - Common traps to avoid
                Say: "Pattern Alert 🎯: Here's what examiners love to test..."
            """
        )
        
        workflow = Workflow(
            name=f"{topic} Practice Session",
            steps=[
                easy_question_step,
                medium_question_step,
                hard_question_step,
                pattern_summary_step
            ]
        )
        
        return workflow
    
    def run_diagnostic(self) -> dict:
        """Run initial diagnostic to assess student level"""
        
        diagnostic_agent = Agent(
            name="Diagnostic Agent",
            model=OpenAIChat(id=PRIMARY_MODEL),
            instructions="""
                Run a quick diagnostic assessment:
                - 10 questions each from Physics, Chemistry, Math
                - Mix of easy, medium, hard
                - Cover high-weightage topics
                
                After each answer, note:
                - Correct/incorrect
                - Time taken
                - Confidence shown
                
                Output: Subject-wise accuracy and weak topic identification
            """
        )
        
        return diagnostic_agent.run(
            "Start the diagnostic assessment for JEE Main preparation"
        )