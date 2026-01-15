#!/usr/bin/env python3
"""
JEE Prep AI Agent System - CLI Entry Point
Built with Agno multi-agent framework
"""

import os
import uuid
import warnings
from datetime import date, datetime
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from agno.models.litellm import LiteLLM

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from jee_agent.storage.database import StudentStorage

from jee_agent.config.settings import (
    DATABASE_URL, 
    EXAM_DATE, 
    OPENAI_API_KEY, 
    MISTRAL_API_KEY, 
    GROQ_API_KEY
)
from jee_agent.storage.student_state import StudentState, SessionLog
from jee_agent.teams.jee_prep_team import create_jee_prep_team
from jee_agent.workflows.study_session import StudySessionWorkflow

# Initialize
app = typer.Typer()
console = Console()

MODEL_MAP = {
    "mistral": {
        "primary": "mistral/mistral-large-latest",
        "fast": "mistral/open-mistral-nemo",
        "fallback": "groq/llama-3.3-70b-versatile"
    },
    "openai": {
        "primary": "openai/gpt-4o",
        "fast": "openai/gpt-4o-mini",
        "fallback": "mistral/mistral-large-latest"
    },
    "groq": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fast": "groq/llama-3.1-8b-instant",
        "fallback": "mistral/mistral-large-latest"
    }
}


def get_db() -> StudentStorage:
    """Get database connection with error handling"""
    try:
        return StudentStorage()
    except Exception as e:
        if "connection refused" in str(e).lower() or "connection to server" in str(e).lower():
            console.print(Panel.fit(
                "[bold red]Cannot connect to Database![/bold red]\n\n"
                "Please ensure PostgreSQL is running via Docker:\n"
                "[cyan]docker compose up -d[/cyan]\n\n"
                f"Error details: {e}",
                title="❌ Connection Error"
            ))
            raise typer.Exit(code=1)
        raise e


def get_or_create_student(student_id: Optional[str] = None) -> StudentState:
    """Load existing student or create new one"""
    db = get_db()
    
    if student_id:
        # Try to load existing
        stored = db.get(student_id)
        if stored:
            return StudentState(**stored)
    else:
        # Try to find last active student for single-user convenience
        stored = db.get_last_student()
        if stored:
            student = StudentState(**stored)
            console.print(f"[green]Welcome back, {student.name}![/green]")
            return student
    
    # Create new student
    console.print(Panel.fit(
        "[bold cyan]Welcome to JEE Prep AI! 🎯[/bold cyan]\n" 
        "Let's set up your personalized preparation system.",
        title="New Student Setup"
    ))
    
    name = Prompt.ask("What's your name?", default="Student")
    target_rank = Prompt.ask("What is your target percentile or rank?", default="99th Percentile")
    
    # Study Schedule
    console.print("\n[bold]Study Schedule Pattern[/bold]")
    weekday_hours = float(Prompt.ask("Hours available on [cyan]Weekdays[/cyan]", default="6"))
    weekend_hours = float(Prompt.ask("Hours available on [cyan]Weekends[/cyan]", default="10"))
    
    # Generate next 8 days schedule (starting today)
    daily_hours = []
    today = date.today().weekday() # 0=Monday, 6=Sunday
    for i in range(8):
        current_day = (today + i) % 7
        if current_day < 5: # Weekday
            daily_hours.append(weekday_hours)
        else: # Weekend
            daily_hours.append(weekend_hours)

    # Initial Confidence
    console.print("\n[bold]Current Confidence (1-10)[/bold]")
    conf_p = int(Prompt.ask("Physics", default="5"))
    conf_c = int(Prompt.ask("Chemistry", default="5"))
    conf_m = int(Prompt.ask("Math", default="5"))
    
    focus = Prompt.ask(
        "\n[bold]Primary Focus[/bold]",
        choices=["Syllabus Completion", "Revision & Practice", "Mock Tests"],
        default="Revision & Practice"
    )
    
    energy_time = Prompt.ask(
        "When do you focus best?",
        choices=["morning", "afternoon", "evening"],
        default="morning"
    )
    
    student = StudentState(
        student_id=str(uuid.uuid4()),
        name=name,
        exam_date=date.fromisoformat(EXAM_DATE),
        daily_hours_available=daily_hours,
        energy_peak_time=energy_time,
        target_rank=target_rank,
        primary_focus=focus
    )
    
    # Initialize topic confidence (simplified mapping)
    # In a real app, we'd map this to specific topics, but for now we set a baseline
    # Note: We aren't setting individual topic confidence here to avoid complexity,
    # but the agents will use the general confidence level context.
    
    # Save to database
    db.upsert(student.student_id, student.model_dump(mode='json'))
    
    return student


def display_status(student: StudentState):
    """Display current preparation status"""
    
    days_left = student.days_remaining()
    overall_acc = student.get_overall_accuracy()
    weak_topics = student.get_weakest_topics(3)
    
    status = f"""
[bold]Days Remaining:[/bold] {days_left}
[bold]Overall Accuracy:[/bold] {overall_acc:.1%}
[bold]Sessions Completed:[/bold] {len(student.sessions)}

[bold red]Weak Topics:[/bold red]
"""
    for topic in weak_topics:
        status += f"  • {topic.topic_name} ({topic.subject}): {topic.accuracy:.1%}\n"
    
    console.print(Panel(status, title=f"📊 {student.name}'s Progress"))


def start_session(student: StudentState):
    """Start a new study session with proper Agno session management"""
    
    # Create session log
    session = SessionLog(
        session_id=str(uuid.uuid4()),
        date=date.today(),
        start_time=datetime.now()
    )
    student.current_session = session
    
    console.print(Panel.fit(
        f"[bold green]Session Started![/bold green]\n" 
        f"Time: {session.start_time.strftime('%H:%M')}\n" 
        f"Days until exam: {student.days_remaining()}",
        title="🚀 New Session"
    ))
    
    # Create team with proper user_id and session_id
    try:
        team = create_jee_prep_team(
            student_id=student.student_id,
            session_id=session.session_id
        )
    except Exception as e:
        # Check for connection refused error
        if "connection refused" in str(e).lower() or "connection to server" in str(e).lower():
            console.print(Panel.fit(
                "[bold red]Cannot connect to Database![/bold red]\n\n"
                "Please ensure PostgreSQL is running via Docker:\n"
                "[cyan]docker compose up -d[/cyan]\n\n"
                f"Error details: {e}",
                title="❌ Connection Error"
            ))
            return
        raise e
    
    # Initial planning context
    planning_context = f"""
    Student: {student.name}
    Target: {student.target_rank}
    Focus: {student.primary_focus}
    Days remaining: {student.days_remaining()}
    Today's available hours: {student.daily_hours_available[0]} (Weekly Pattern set)
    Energy peak: {student.energy_peak_time}
    Overall accuracy: {student.get_overall_accuracy():.1%}
    Weakest topics: {[t.topic_name for t in student.get_weakest_topics(5)]}
    Previous sessions: {len(student.sessions)}
    """
    
    # Get today's plan with proper session context
    console.print("\n[cyan]Generating your personalized plan for today...[/cyan]\n")
    team.print_response(
        f"Create today's study plan based on this context:\n{planning_context}",
        stream=True,
        user_id=student.student_id,
        session_id=session.session_id
    )
    
    # Main interaction loop
    console.print("\n[green]Ready to start! Type your questions or responses below.[/green]")
    console.print("[dim]Commands: /plan (show plan), /progress (show progress), /break (take break), /model <provider>, /quit (end session)[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Handle commands
            if user_input.lower() == "/quit":
                break
            elif user_input.lower().startswith("/model"):
                parts = user_input.split()
                if len(parts) < 2:
                    console.print("[red]Usage: /model <provider> (mistral, openai, groq)[/red]")
                    continue
                
                provider = parts[1].lower()
                if provider not in MODEL_MAP:
                    console.print(f"[red]Unsupported provider: {provider}. Use: mistral, openai, or groq.[/red]")
                    continue
                
                # Check for API keys
                if provider == "openai" and not OPENAI_API_KEY:
                    console.print("[red]Error: OPENAI_API_KEY not found in environment.[/red]")
                    continue
                if provider == "mistral" and not MISTRAL_API_KEY:
                    console.print("[red]Error: MISTRAL_API_KEY not found in environment.[/red]")
                    continue
                if provider == "groq" and not GROQ_API_KEY:
                    console.print("[red]Error: GROQ_API_KEY not found in environment.[/red]")
                    continue

                new_models = MODEL_MAP[provider]
                
                # Update team leader
                team.model = LiteLLM(
                    id=new_models["primary"],
                    request_params={"fallbacks": [new_models["fallback"]]}
                )
                
                # Update all members
                for member in team.members:
                    # Wellbeing Guardian and Learning Memory Curator get the fast model
                    if member.name in ["Wellbeing Guardian", "Learning Memory Curator", "Lecture Flow Controller"]:
                        member.model = LiteLLM(id=new_models["fast"])
                    else:
                        member.model = LiteLLM(id=new_models["primary"])
                
                console.print(Panel(
                    f"[green]Switched to [bold]{provider.upper()}[/bold] provider[/green]\n"
                    f"[dim]Primary Model: {new_models['primary']}\n"
                    f"Fast Model: {new_models['fast']}[/dim]",
                    title="🤖 Model Provider Updated"
                ))
                continue
            elif user_input.lower() == "/plan":
                team.print_response(
                    "Show me today's remaining plan",
                    user_id=student.student_id,
                    session_id=session.session_id
                )
                continue
            elif user_input.lower() == "/progress":
                display_status(student)
                continue
            elif user_input.lower() == "/break":
                console.print("[yellow]Taking a 5-minute break. You've earned it! ☕[/yellow]")
                continue
            
            # Normal interaction with proper session context
            team.print_response(
                user_input,
                stream=True,
                user_id=student.student_id,
                session_id=session.session_id
            )
            
        except KeyboardInterrupt:
            break
    
    # End session
    end_session(student)


def end_session(student: StudentState):
    """End the current session and save progress"""
    
    if student.current_session:
        student.current_session.end_time = datetime.now()
        duration = (student.current_session.end_time - student.current_session.start_time)
        student.current_session.duration_mins = int(duration.total_seconds() / 60)
        
        student.sessions.append(student.current_session)
        student.current_session = None
        
        # Save to database
        get_db().upsert(student.student_id, student.model_dump(mode='json'))
        
        console.print(Panel.fit(
            f"[bold green]Session Complete![/bold green]\n" 
            f"Duration: {duration.total_seconds() / 60:.0f} minutes\n" 
            f"Great work! See you tomorrow. 💪",
            title="✅ Session Ended"
        ))


@app.command()
def start(student_id: Optional[str] = None):
    """Start the JEE Prep AI system"""
    
    console.print(Panel.fit(
        "[bold cyan]JEE PREP AI SYSTEM[/bold cyan]\n" 
        "Powered by Agno Multi-Agent Framework",
        title="🎓 Welcome"
    ))
    
    # Load or create student
    student = get_or_create_student(student_id)
    
    # Show current status
    display_status(student)
    
    # Ask what to do
    action = Prompt.ask(
        "\nWhat would you like to do?",
        choices=["study", "diagnostic", "progress", "quit"],
        default="study"
    )
    
    if action == "study":
        start_session(student)
    elif action == "diagnostic":
        console.print("[cyan]Starting diagnostic assessment...[/cyan]")
        workflow = StudySessionWorkflow(student)
        workflow.run_diagnostic()
    elif action == "progress":
        display_status(student)
    else:
        console.print("[yellow]Goodbye! Come back soon.[/yellow]")


@app.command()
def reset():
    """Reset all student data (use with caution)"""
    if Confirm.ask("[red]This will delete ALL student data. Are you sure?[/red]"):
        try:
            get_db().clear()
            console.print("[green]Data reset complete.[/green]")
        except Exception as e:
            console.print(f"[red]Error resetting data: {e}[/red]")
