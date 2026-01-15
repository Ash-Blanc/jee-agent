# JEE Prep AI Agent System

An adaptive, multi-agent AI system for JEE Main 2026 preparation built with [Agno](https://docs.agno.com).

## Features

- **Adaptive Learning**: Personalized study plans based on your performance
- **Smart PYQ Curation**: AI-powered question selection matching your level
- **Just-in-Time Theory**: Micro-theory injections when you're stuck
- **Stress Monitoring**: Wellbeing guardian prevents burnout
- **Memory System**: Learns your patterns and preferences over time
- **Lecture Optimization**: Smart speed recommendations and timestamp navigation

## Architecture

Built using Agno's multi-agent framework:

- **Team Coordination**: JEE Prep Team with 6 specialized agents
- **Persistent Memory**: SQLite-backed session and user memory
- **Knowledge Base**: Vector-powered PYQ search with LanceDB
- **Structured Outputs**: Type-safe responses using Pydantic models
- **Session Management**: Multi-user support with proper state isolation

## Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key

### Installation

```bash
# Install dependencies
pip install -U agno openai python-dotenv typer rich pydantic lancedb

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Run

```bash
python main.py start
```

## Project Structure

```
├── agents/              # Specialized AI agents
│   ├── daily_planner.py
│   ├── pyq_curator.py
│   ├── theory_coach.py
│   ├── lecture_optimizer.py
│   ├── stress_monitor.py
│   └── memory_curator.py
├── teams/               # Multi-agent teams
│   └── jee_prep_team.py
├── workflows/           # Deterministic workflows
│   └── study_session.py
├── knowledge/           # Knowledge bases
│   └── pyq_loader.py
├── storage/             # State management
│   └── student_state.py
├── config/              # Configuration
│   └── settings.py
├── data/                # Data files
│   ├── pyqs/           # Previous year questions
│   └── syllabus/       # JEE syllabus
└── main.py             # Entry point
```

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
    vector_db=LanceDb(
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
python main.py start
```

### Continue Previous Session

```bash
python main.py start --student-id <your-student-id>
```

### Reset Data

```bash
python main.py reset
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
