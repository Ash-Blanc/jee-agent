# Quick Reference: Agno Best Practices

## Essential Patterns

### 1. Creating a Team with Proper Configuration

```python
from agno.team import Team
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

db = SqliteDb(table_name="sessions", db_file="data/app.db")

team = Team(
    name="My Team",
    model=OpenAIChat(id="gpt-4o"),
    members=[agent1, agent2, agent3],
    # Database for persistence
    db=db,
    # Memory management
    enable_user_memories=True,
    enable_agentic_memory=True,
    # Session configuration
    user_id="user_123",
    session_id="session_456",
    # UI configuration
    markdown=True,
    show_tool_calls=False,
    show_members_responses=True,
    # Instructions
    instructions="How the team should coordinate..."
)
```

### 2. Running Team with Session Context

```python
# Always pass user_id and session_id
team.print_response(
    "Your message here",
    stream=True,
    user_id="user_123",
    session_id="session_456"
)

# Or use run() for programmatic access
response = team.run(
    "Your message",
    user_id="user_123",
    session_id="session_456"
)
```

### 3. Creating Agent with Structured Output

```python
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat

class MyOutput(BaseModel):
    """Structured output schema"""
    title: str = Field(description="The title")
    items: List[str] = Field(description="List of items")
    score: float = Field(description="Score from 0-1", ge=0.0, le=1.0)

agent = Agent(
    name="My Agent",
    model=OpenAIChat(id="gpt-4o"),
    output_schema=MyOutput,  # Type-safe responses
    instructions="Your instructions..."
)

# Response is automatically parsed
response = agent.run("Generate something")
output = response.content  # MyOutput object
print(output.title)
print(output.items)
```

### 4. Agent with Knowledge Base (Agentic RAG)

```python
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder

# Create knowledge base
knowledge = Knowledge(
    vector_db=LanceDb(
        uri="data/vector_store",
        table_name="documents",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    )
)

# Add content
knowledge.add_content(url="https://example.com/docs")
knowledge.add_content(path="data/documents/")

# Create agent with knowledge
agent = Agent(
    name="RAG Agent",
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge,
    search_knowledge=True,  # Enables agentic RAG
    instructions=[
        "Always search your knowledge before answering",
        "Include sources in your response"
    ]
)
```

### 5. Agent with Memory Tools

```python
from agno.tools.memory import MemoryTools

agent = Agent(
    name="Memory Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[MemoryTools(add_instructions=True)],
    instructions="Use memory tools to remember user preferences"
)

# Agent can now:
# - think() about what to remember
# - add_memory() to store information
# - get_memory() to retrieve information
# - update_memory() to modify existing memories
# - delete_memory() to remove outdated info
# - analyze() to verify memory operations
```

### 6. Multi-User Session Management

```python
# User 1
team.print_response(
    "My name is Alice",
    user_id="alice@example.com",
    session_id="alice_session_1"
)

# User 2 (completely isolated)
team.print_response(
    "My name is Bob",
    user_id="bob@example.com",
    session_id="bob_session_1"
)

# Continue Alice's session later
team.print_response(
    "What's my name?",
    user_id="alice@example.com",
    session_id="alice_session_1"
)
# Will remember "Alice"
```

### 7. Async Operations

```python
import asyncio

async def main():
    # Async run
    response = await team.arun(
        "Your message",
        user_id="user_123",
        session_id="session_456"
    )
    
    # Async streaming
    async for event in team.arun(
        "Your message",
        stream=True,
        stream_events=True,
        user_id="user_123",
        session_id="session_456"
    ):
        print(event)

asyncio.run(main())
```

## Common Patterns

### Pattern: Router Team (Passthrough)

```python
team = Team(
    name="Router Team",
    members=[
        Agent(name="English Agent", role="Handle English queries"),
        Agent(name="Spanish Agent", role="Handle Spanish queries"),
    ],
    respond_directly=True,  # Members respond directly
    determine_input_for_members=False,  # Pass input unchanged
)
```

### Pattern: Coordinator Team

```python
team = Team(
    name="Coordinator Team",
    members=[researcher, writer, reviewer],
    respond_directly=False,  # Team leader synthesizes responses
    instructions="""
        1. Researcher gathers information
        2. Writer creates content
        3. Reviewer checks quality
        4. Synthesize final response
    """
)
```

### Pattern: Workflow for Deterministic Flow

```python
from agno.workflow import Workflow

workflow = Workflow(
    name="Study Workflow",
    steps=[
        planning_agent,      # Step 1: Plan
        practice_agent,      # Step 2: Practice
        review_agent,        # Step 3: Review
    ]
)

workflow.print_response("Start study session", markdown=True)
```

## Database Options

### SQLite (Local)
```python
from agno.db.sqlite import SqliteDb
db = SqliteDb(table_name="sessions", db_file="data/app.db")
```

### PostgreSQL (Production)
```python
from agno.db.postgres import PostgresDb
db = PostgresDb(db_url="postgresql+psycopg://user:pass@localhost:5432/db")
```

### In-Memory (Testing)
```python
from agno.db.in_memory import InMemoryDb
db = InMemoryDb()
```

## Model Options

### OpenAI
```python
from agno.models.openai import OpenAIChat

# GPT-4o (best quality)
model = OpenAIChat(id="gpt-4o")

# GPT-4o-mini (fast & cheap)
model = OpenAIChat(id="gpt-4o-mini")

# With custom settings
model = OpenAIChat(
    id="gpt-4o",
    temperature=0.7,
    max_tokens=2000
)
```

### Anthropic Claude
```python
from agno.models.anthropic import Claude

model = Claude(id="claude-sonnet-4-20250514")
```

### Groq (Fast Inference)
```python
from agno.models.groq import Groq

model = Groq(id="llama-3.3-70b-versatile")
```

## Tools

### Built-in Tools
```python
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.youtube import YouTubeTools
from agno.tools.exa import ExaTools

agent = Agent(
    tools=[
        DuckDuckGoTools(),
        HackerNewsTools(),
        YouTubeTools(),
    ]
)
```

### Reasoning Tools
```python
from agno.tools.reasoning import ReasoningTools
from agno.tools.knowledge import KnowledgeTools
from agno.tools.memory import MemoryTools

agent = Agent(
    tools=[
        ReasoningTools(add_instructions=True),
        KnowledgeTools(knowledge=kb, add_instructions=True),
        MemoryTools(add_instructions=True),
    ]
)
```

### Custom Tools
```python
def my_tool(param1: str, param2: int) -> str:
    """Tool description for the AI"""
    return f"Result: {param1} x {param2}"

agent = Agent(
    tools=[my_tool]
)
```

## Error Handling

```python
from agno.exceptions import AgentRunError

try:
    response = agent.run("Your message")
except AgentRunError as e:
    print(f"Error: {e}")
    # Handle error
```

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Show Tool Calls
```python
team = Team(
    show_tool_calls=True,  # See what tools are being called
    show_members_responses=True,  # See which agent responds
)
```

### Access Run Metrics
```python
response = agent.run("Your message")
print(f"Tokens used: {response.metrics.input_tokens + response.metrics.output_tokens}")
print(f"Time taken: {response.metrics.time_to_first_token}s")
```

## Best Practices Checklist

- [ ] Always pass `user_id` and `session_id` to team.run()
- [ ] Use `SqliteDb` not `SqliteStorage`
- [ ] Enable `enable_user_memories=True` for personalization
- [ ] Use `output_schema` for type-safe responses
- [ ] Use `search_knowledge=True` for agentic RAG
- [ ] Use fast models (gpt-4o-mini) for monitoring agents
- [ ] Use structured outputs (Pydantic) for complex data
- [ ] Set `markdown=True` for better formatting
- [ ] Add clear `instructions` to agents and teams
- [ ] Use `stream=True` for better UX
- [ ] Test multi-user isolation
- [ ] Handle errors gracefully

## Common Mistakes to Avoid

❌ **Don't:** Forget user_id and session_id
```python
team.print_response("Hello")  # BAD
```

✅ **Do:** Always include them
```python
team.print_response("Hello", user_id=uid, session_id=sid)  # GOOD
```

---

❌ **Don't:** Use deprecated parameters
```python
team = Team(mode="coordinate")  # BAD - deprecated
```

✅ **Do:** Use new configuration
```python
team = Team(enable_user_memories=True)  # GOOD
```

---

❌ **Don't:** Parse unstructured text manually
```python
response = agent.run("Create plan")
text = response.content
# Now parse text manually... BAD
```

✅ **Do:** Use structured outputs
```python
agent = Agent(output_schema=Plan)
response = agent.run("Create plan")
plan = response.content  # Already parsed! GOOD
```

---

❌ **Don't:** Share sessions between users
```python
team.print_response("Alice's message", session_id="shared")
team.print_response("Bob's message", session_id="shared")  # BAD
```

✅ **Do:** Use separate sessions
```python
team.print_response("Alice's message", user_id="alice", session_id="alice_s1")
team.print_response("Bob's message", user_id="bob", session_id="bob_s1")  # GOOD
```

## Quick Links

- [Agno Docs](https://docs.agno.com)
- [Teams Guide](https://docs.agno.com/basics/teams/overview)
- [Agents Guide](https://docs.agno.com/basics/agents/overview)
- [Workflows Guide](https://docs.agno.com/basics/workflows/overview)
- [Memory Guide](https://docs.agno.com/basics/memory/team/overview)
- [Knowledge Guide](https://docs.agno.com/basics/knowledge/knowledge-bases)
- [Structured Outputs](https://docs.agno.com/basics/input-output/overview)
- [Session Management](https://docs.agno.com/basics/sessions/session-management)

---

**Pro Tip:** Start simple, then add complexity. Begin with a single agent, then team, then add memory, knowledge, and structured outputs as needed.
