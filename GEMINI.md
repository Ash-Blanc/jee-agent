# JEE Prep AI Agent System

## Project Overview

The **JEE Prep AI Agent System** is an adaptive, multi-agent CLI application designed to assist students in preparing for the JEE Main 2026 examination. Built using the **Agno** framework, it orchestrates a team of specialized AI agents to provide personalized study plans, question curation, just-in-time theory coaching, and stress monitoring.

### Core Architecture

*   **Framework:** Agno (v2.2.0+)
*   **Entry Point:** `main.py` (CLI application using Typer and Rich)
*   **Team:** `JEE Adaptive Learning System` (defined in `app/teams/jee_prep_team.py`)
*   **Agents:**
    *   `DailyPlannerAgent`: Schedules study sessions.
    *   `PYQCuratorAgent`: Selects Previous Year Questions (PYQs) using vector search.
    *   `TheoryCoachAgent`: Provides explanations when students get stuck.
    *   `LectureOptimizerAgent`: Optimizes content consumption.
    *   `StressMonitorAgent`: Monitors student well-being.
    *   `MemoryCuratorAgent`: Manages long-term student memory.
*   **Data Storage:**
    *   **Relational:** PostgreSQL (configured via `DATABASE_URL`) for student profiles and session logs.
    *   **Vector:** LanceDB (`data/vector_store`) for semantic search over PYQs.
*   **Configuration:** Centralized in `app/config/settings.py`.

## Building and Running

### Prerequisites

*   Python 3.13+
*   OpenAI API Key

### Installation

1.  **Install Dependencies:**
    ```bash
    pip install -U agno openai python-dotenv typer rich pydantic lancedb sqlalchemy
    ```
    *Note: `pyproject.toml` also lists `hatchling` for building.*

2.  **Environment Setup:**
    ```bash
    cp .env.example .env
    # Edit .env and add your OPENAI_API_KEY
    ```

### Execution Commands

*   **Start the Application:**
    ```bash
    python main.py start
    ```
    *Optionally provide a student ID to resume:*
    ```bash
    python main.py start --student-id <uuid>
    ```

*   **Reset Data:**
    ```bash
    python main.py reset
    ```

*   **Run as Script (via pyproject.toml):**
    ```bash
    jee-prep start
    ```

## Development Conventions

*   **Code Style:**
    *   **Formatting:** `black` (line length: 100).
    *   **Linting:** `ruff` (target version: py313).
    *   **Type Checking:** `mypy` (strict typing enforced).
*   **Agent Development:**
    *   New agents should be added to `app/agents/`.
    *   Agents must be registered in the `create_jee_prep_team` function in `app/teams/jee_prep_team.py`.
*   **State Management:**
    *   Use `StudentState` (Pydantic model) for managing user context.
    *   Agno's `SqliteDb` is used for session persistence; ensure `user_id` and `session_id` are passed to agent interactions.
*   **Data Models:**
    *   All data structures (PYQs, Student State, Plans) should be defined as Pydantic models.
