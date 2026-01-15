# JEE Prep AI Agent System

An adaptive, multi-agent AI system for JEE Main 2026 preparation built with [Agno](https://docs.agno.com).

## 🚀 Key Features

### 🧠 Specialized Multi-Agent Team
Orchestrates a team of 6 specialized AI agents, each with a distinct role in your preparation:
*   **Daily Planner**: Generates adaptive study schedules based on your target hours, energy peaks, and exam weightage.
*   **PYQ Curator**: Dynamically serves Previous Year Questions using vector search (PgVector), adjusting difficulty (Easy → Medium → Hard) based on your performance.
*   **Theory Coach**: Provides just-in-time micro-theory explanations only when you've been stuck for more than 2 minutes.
*   **Lecture Optimizer**: Recommends optimal watch speeds and key timestamps for JEE lectures to maximize content retention.
*   **Stress Monitor**: Background well-being guardian that detects burnout signals and suggests breaks or session adjustments.
*   **Memory Curator**: Manages long-term student state, extracting behavioral patterns, breakthroughs, and struggle points from every interaction.

### 📊 Adaptive Progress Tracking
*   **Student State Persistence**: Complete history of sessions, topic-wise accuracy, and confidence levels stored in PostgreSQL.
*   **Diagnostic Assessment**: Structured workflow to identify your strengths and weaknesses across Physics, Chemistry, and Mathematics.
*   **Pattern Recognition**: Identifies high-weightage topics where you're losing marks and adjusts your learning path accordingly.

### 🛠️ Production-Ready Infrastructure
*   **AgentOS Integration**: Fully compatible with Agno's AgentOS for managing, monitoring, and scaling your agentic system.
*   **Session Isolation**: Multi-user support with rigorous session management for consistent and personalized experiences.
*   **Vector Knowledge Base**: Hybrid search over thousands of PYQs with PgVector for lightning-fast, semantically relevant question retrieval.

### 💻 Interactive CLI
*   Beautiful terminal interface built with **Rich** and **Typer**.
*   Real-time streaming responses from the agent team.
*   Intuitive commands for planning, progress tracking, and session management.

## Architecture

Built using Agno's multi-agent framework:

- **Team Coordination**: JEE Prep Team with 6 specialized agents
- **Persistent Memory**: PostgreSQL-backed session and user memory
- **Knowledge Base**: Vector-powered PYQ search with PgVector
- **Structured Outputs**: Type-safe responses using Pydantic models
- **Session Management**: Multi-user support with proper state isolation

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended)
- PostgreSQL with PgVector (see [PostgreSQL Setup](#postgresql-setup))
- API Keys (OpenAI, Mistral, or Groq)

### Installation

We recommend using `uv` for fast and reliable dependency management.

```bash
# 1. Create virtual environment and install dependencies
uv sync

# 2. Install the CLI tool in editable mode (optional, for direct 'jee-prep' access)
uv tool install -e .

# 3. Set up environment
cp .env.example .env
# Edit .env and add your API keys and DATABASE_URL
```

### Running

**CLI Application:**

```bash
# using the installed tool
jee-prep start

# Or using uv run
uv run jee-prep start
```

*Optionally provide a student ID to resume:*
```bash
jee-prep start --student-id <uuid>
```

**AgentOS (Web Backend):**

```bash
# Start the AgentOS process (for UI connection)
uv run -m jee_agent.os
```

### Development

Use the following commands to maintain code quality:

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type check
uv run mypy .
```

## Project Structure

```
├── jee_agent/           # Core application package
│   ├── agents/          # Specialized AI agents
│   │   ├── daily_planner.py
│   │   ├── pyq_curator.py
│   │   ├── theory_coach.py
│   │   ├── lecture_optimizer.py
│   │   ├── stress_monitor.py
│   │   └── memory_curator.py
│   ├── teams/           # Multi-agent teams
│   │   └── jee_prep_team.py
│   ├── workflows/       # Deterministic workflows
│   │   └── study_session.py
│   ├── knowledge/       # Knowledge bases
│   │   └── pyq_loader.py
│   ├── storage/         # State management
│   │   ├── database.py  # Database connection
│   │   └── student_state.py
│   ├── config/          # Configuration
│   ├── data/            # Data files (PYQs, Syllabus)
│   ├── cli.py           # CLI application logic
│   ├── os.py            # AgentOS definition
│   └── main.py          # Entry point
├── data/                # Local database storage
├── pyproject.toml       # Project metadata and dependencies
└── .env                 # Environment variables
```

## 🖥️ Running the UI

This project uses the official [Agno Agent UI](https://github.com/agno-agi/agent-ui) for a beautiful graphical interface.

1.  **Start the Backend (AgentOS)**
    ```bash
    # From the project root
    uv run -m jee_agent.os
    ```
    This starts the API server (default: `http://localhost:8000`).

2.  **Setup & Run the Frontend**
    ```bash
    # Clone the UI repo (if you haven't already)
    git clone https://github.com/agno-agi/agent-ui agent-ui

    # Enter directory
    cd agent-ui

    # Install dependencies
    npm install

    # Start the development server
    npm run dev
    ```
    The UI will typically start at `http://localhost:3000`. Open this in your browser and connect to your local backend.

## Key Concepts

### Multi-Agent Team

The system uses Agno's Team abstraction with coordinated agents:

```python
team = Team(
    name="JEE Adaptive Learning System",
    members=[daily_planner, pyq_curator, theory_coach, ...],
    db=db,
    enable_user_memories=True,
    user_id=student_id
)
```

### Knowledge Base

PYQs are stored in a vector database for semantic search:

```python
knowledge = Knowledge(
    vector_db=PgVector(
        db_url=DATABASE_URL,
        table_name="jee_pyqs",
        search_type=SearchType.hybrid
    )
)
```

### Session Management

Proper user and session isolation:

```python
team.print_response(
    message,
    user_id=student_id,
    session_id=session_id,
    stream=True
)
```

## Usage

### Start a Study Session

```bash
jee-prep start
```

### Continue Previous Session

```bash
jee-prep start --student-id <your-student-id>
```

### Reset Data

```bash
jee-prep reset
```

## Configuration

Edit `config/settings.py`:

- `PRIMARY_MODEL`: Main model for complex reasoning (default: gpt-4o)
- `FAST_MODEL`: Fast model for monitoring (default: gpt-4o-mini)
- `EXAM_DATE`: Your JEE Main exam date
- `DEFAULT_DAILY_HOURS`: Study hours per day

## Data

### PYQ Format

```json
{
  "id": "pyq_001",
  "question_text": "...",
  "options": ["A", "B", "C", "D"],
  "correct_answer": "B",
  "year": 2024,
  "subject": "physics",
  "topic": "mechanics",
  "difficulty": "medium",
  "frequency_score": 0.85
}
```

## Best Practices Implemented

Based on [Agno documentation](https://docs.agno.com):

1. **Structured Outputs**: Using Pydantic models for type safety
2. **Session Management**: Proper user_id and session_id handling
3. **Memory Management**: Enable user memories for personalization
4. **Knowledge Integration**: Agentic RAG with vector search
5. **Team Coordination**: Clear delegation rules and handoffs
6. **Error Handling**: Graceful degradation and recovery

## Contributing

Contributions welcome! Please ensure:

- Type hints on all functions
- Pydantic models for data structures
- Proper session management
- Tests for new features

## License

MIT

## Acknowledgments

Built with [Agno](https://docs.agno.com) - The AI Agent Framework
