# JEE Prep AI Agent System

## Project Overview

The **JEE Prep AI Agent System** is an adaptive, multi-agent CLI application designed to assist students in preparing for the JEE Main 2026 examination. Built using the **Agno** framework, it orchestrates a team of specialized AI agents to provide personalized study plans, question curation, just-in-time theory coaching, and stress monitoring.

### Core Architecture

*   **Framework:** Agno (v2.2.0+)
*   **Entry Point:** `jee_agent/cli.py` (CLI application using Typer and Rich)
*   **Team:** `JEE Adaptive Learning System` (defined in `jee_agent/teams/jee_prep_team.py`)
*   **Agents:**
    *   `DailyPlannerAgent`: Schedules study sessions.
    *   `PYQCuratorAgent`: Selects Previous Year Questions (PYQs) using vector search.
    *   `TheoryCoachAgent`: Provides explanations when students get stuck.
    *   `LectureOptimizerAgent`: Optimizes content consumption.
    *   `StressMonitorAgent`: Monitors student well-being.
    *   `MemoryCuratorAgent`: Manages long-term student memory.
*   **Data Storage:** PostgreSQL-only architecture (configured via `DATABASE_URL`)
    *   **Agent Storage:** `PostgresDb` for agent sessions and memory
    *   **Vector Search:** `PgVector` for semantic search over PYQs
    *   **Student Data:** Custom `StudentStorage` class with JSONB
*   **Configuration:** Centralized in `jee_agent/config/settings.py`
*   **Database Module:** Centralized in `jee_agent/database.py`

## Building and Running

### Prerequisites

*   Python 3.13+
*   PostgreSQL with PgVector extension
*   API Keys: Mistral, OpenAI, or Groq

### PostgreSQL Setup

Run PgVector using Docker:
```bash
docker run -d \
  -e POSTGRES_DB=jee_agent \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5432:5432 \
  --name pgvector \
  agnohq/pgvector:16
```

### Installation

1.  **Install Dependencies:**
    ```bash
    uv sync
    # Or with pip:
    pip install -e .
    ```

2.  **Environment Setup:**
    ```bash
    cp .env.example .env
    # Edit .env and add your API keys and DATABASE_URL
    ```

### Execution Commands

*   **Start the Application:**
    ```bash
    uv run python -m jee_agent.cli start
    ```
    *Optionally provide a student ID to resume:*
    ```bash
    uv run python -m jee_agent.cli start --student-id <uuid>
    ```

*   **Reset Data:**
    ```bash
    uv run python -m jee_agent.cli reset
    ```

*   **Run AgentOS (Web UI):**
    ```bash
    uv run python -m jee_agent.os
    ```

## Development Conventions

*   **Code Style:**
    *   **Formatting:** `black` (line length: 100).
    *   **Linting:** `ruff` (target version: py313).
    *   **Type Checking:** `mypy` (strict typing enforced).
*   **Agent Development:**
    *   New agents should be added to `jee_agent/agents/`.
    *   Agents must be registered in the `create_jee_prep_team` function in `jee_agent/teams/jee_prep_team.py`.
*   **Database Access:**
    *   Use `jee_agent/database.py` for all database operations.
    *   Use `agent_db` for Agno agent/team sessions.
    *   Use `StudentStorage` for custom student state.
*   **State Management:**
    *   Use `StudentState` (Pydantic model) for managing user context.
    *   Agno's `PostgresDb` is used for session persistence.
*   **Data Models:**
    *   All data structures (PYQs, Student State, Plans) should be defined as Pydantic models.
