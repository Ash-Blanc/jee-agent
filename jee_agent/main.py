#!/usr/bin/env python3
"""
JEE Prep AI Agent System - Main Entry Point
Built with Agno multi-agent framework

Run with: python main.py start
"""

import os
import uuid
from datetime import date, datetime
from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from jee_agent.storage.db import StudentStorage

from jee_agent.config.settings import DATABASE_URL, EXAM_DATE
from jee_agent.storage.student_state import StudentState, SessionLog
from jee_agent.teams.jee_prep_team import create_jee_prep_team
from jee_agent.workflows.study_session import StudySessionWorkflow

# Initialize
app = typer.Typer()
console = Console()

# Use custom Postgres storage for student state
db = StudentStorage()


def get_or_create_student(student_id: Optional[str] = None) -> StudentState:
    """Load existing student or create new one"""
    
    if student_id:
        # Try to load existing
        stored = db.get(student_id)
        if stored:
            return StudentState(**stored)
    
    # Create new student
    console.print(Panel.fit(
        "[bold cyan]Welcome to JEE Prep AI! 🎯[/bold cyan]\n"
        "Let's set up your personalized preparation system.",
        title="New Student Setup"
    ))
    
    name = Prompt.ask("What's your name?", default="Student")
    
    daily_hours = []
    console.print("\n[yellow]How many hours can you study each day until the exam?[/yellow]")
    for i in range(8):
        hours = float(Prompt.ask(f"Day {i+1}", default="10"))
        daily_hours.append(hours)
    
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
        energy_peak_time=energy_time
    )
    
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
    team = create_jee_prep_team(
        student_id=student.student_id,
        session_id=session.session_id
    )
    
    # Initial planning context
    planning_context = f"""
    Student: {student.name}
    Days remaining: {student.days_remaining()}
    Today's available hours: {student.daily_hours_available}
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
    console.print("[dim]Commands: /plan (show plan), /progress (show progress), /break (take break), /quit (end session)[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            # Handle commands
            if user_input.lower() == "/quit":
                break
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
        db.upsert(student.student_id, student.model_dump(mode='json'))
        
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
            db.clear()
            console.print("[green]Data reset complete.[/green]")
        except Exception as e:
            console.print(f"[red]Error resetting data: {e}[/red]")


if __name__ == "__main__":
    app()