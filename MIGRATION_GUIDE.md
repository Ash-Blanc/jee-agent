# Migration Guide: Upgrading to Agno Best Practices

This guide helps you migrate from the old implementation to the improved Agno-based system.

## Quick Start

If you're starting fresh, just run:

```bash
# Install dependencies
pip install -U agno openai python-dotenv typer rich pydantic lancedb

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the system
python main.py start
```

## For Existing Users

### Step 1: Update Dependencies

```bash
pip install -U agno>=2.2.0
```

### Step 2: Database Migration

The database structure has changed. You have two options:

#### Option A: Fresh Start (Recommended)
```bash
python main.py reset
```

#### Option B: Manual Migration
```python
# Old database location
old_db = "data/jee_student.db"

# New database uses SqliteDb instead of SqliteStorage
# Sessions are now stored in a separate table
# Run this migration script:

from agno.db.sqlite import SqliteDb
from agno.storage.sqlite import SqliteStorage

# Load old data
old_storage = SqliteStorage(table_name="students", db_file=old_db)
students = old_storage.get_all()

# Save to new format
new_db = SqliteDb(table_name="students", db_file=old_db)
for student_id, data in students.items():
    new_db.upsert(student_id, data)
```

### Step 3: Update Your Code

#### If you're calling the team directly:

**Before:**
```python
from teams.jee_prep_team import create_jee_prep_team

team = create_jee_prep_team(student_id)
team.print_response("Hello", stream=True)
```

**After:**
```python
from teams.jee_prep_team import create_jee_prep_team
import uuid

session_id = str(uuid.uuid4())
team = create_jee_prep_team(
    student_id=student_id,
    session_id=session_id
)
team.print_response(
    "Hello",
    stream=True,
    user_id=student_id,
    session_id=session_id
)
```

### Step 4: Verify Structured Outputs

If you're processing agent responses programmatically:

**Before:**
```python
response = agent.run("Create a plan")
# response.content is a string, need to parse manually
plan_text = response.content
```

**After:**
```python
response = agent.run("Create a plan")
# response.content is a DailyPlan object
plan = response.content
print(f"Total hours: {plan.total_hours}")
print(f"Focus subject: {plan.focus_subject}")
for block in plan.time_blocks:
    print(f"{block.start_time} - {block.end_time}: {block.subject}")
```

### Step 5: Test Multi-User Support

```python
# Test with multiple students
student1 = "alice@example.com"
student2 = "bob@example.com"

# Each gets their own session
team1 = create_jee_prep_team(student1, "session_1")
team2 = create_jee_prep_team(student2, "session_2")

# Memories are isolated
team1.print_response("My name is Alice", user_id=student1, session_id="session_1")
team2.print_response("My name is Bob", user_id=student2, session_id="session_2")

# Verify isolation
team1.print_response("What's my name?", user_id=student1, session_id="session_1")
# Should say "Alice", not "Bob"
```

## Breaking Changes

### 1. Database Import
```python
# Old
from agno.storage.sqlite import SqliteStorage

# New
from agno.db.sqlite import SqliteDb
```

### 2. Team Creation
```python
# Old
team = Team(mode="coordinate", memory=shared_memory)

# New
team = Team(
    enable_user_memories=True,
    enable_agentic_memory=True,
    db=db
)
# Note: 'mode' parameter is deprecated
```

### 3. Session Management
```python
# Old
team.print_response(message)

# New
team.print_response(
    message,
    user_id=student_id,
    session_id=session_id
)
```

### 4. Agent Responses
```python
# Old - unstructured text
response = agent.run("Create plan")
text = response.content  # string

# New - structured Pydantic models
response = agent.run("Create plan")
plan = response.content  # DailyPlan object
```

## New Features Available

### 1. Agentic Memory
The AI now intelligently manages memories:

```python
team = Team(
    enable_agentic_memory=True,
    # AI decides when to create/update/delete memories
)
```

### 2. Structured Outputs
Type-safe responses:

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    field1: str
    field2: int

agent = Agent(output_schema=MyOutput)
response = agent.run("...")
assert isinstance(response.content, MyOutput)
```

### 3. Memory Tools
Intelligent memory operations:

```python
from agno.tools.memory import MemoryTools

agent = Agent(
    tools=[MemoryTools(add_instructions=True)]
    # Agent can think → add_memory → analyze
)
```

### 4. Session Continuations
Continue conversations across sessions:

```python
# Session 1
team.print_response("Hello", user_id="alice", session_id="s1")

# Later, same session
team.print_response("Continue", user_id="alice", session_id="s1")
# Context is preserved
```

## Troubleshooting

### Issue: "mode parameter is deprecated"
**Solution:** Remove the `mode` parameter from Team creation.

### Issue: "SqliteStorage not found"
**Solution:** Update to `SqliteDb`:
```python
from agno.db.sqlite import SqliteDb
```

### Issue: "Session not persisting"
**Solution:** Ensure you're passing `user_id` and `session_id`:
```python
team.print_response(msg, user_id=uid, session_id=sid)
```

### Issue: "Memories leaking between users"
**Solution:** Always pass unique `user_id` for each user:
```python
team.print_response(msg, user_id="unique_user_id", session_id=sid)
```

### Issue: "Can't parse agent response"
**Solution:** Use structured outputs:
```python
agent = Agent(output_schema=MyModel)
response = agent.run("...")
data = response.content  # Already parsed as MyModel
```

## Performance Tips

1. **Use Fast Models for Monitoring**
   ```python
   stress_monitor = Agent(model=OpenAIChat(id="gpt-4o-mini"))
   ```

2. **Enable Session Summaries** (for long conversations)
   ```python
   team = Team(enable_session_summaries=True)
   ```

3. **Batch Knowledge Searches**
   ```python
   agent = Agent(
       knowledge=kb,
       search_knowledge=True,
       # Agent searches on-demand, not every message
   )
   ```

4. **Use Async for Parallel Operations**
   ```python
   response = await team.arun(message, user_id=uid, session_id=sid)
   ```

## Getting Help

- **Documentation**: https://docs.agno.com
- **Examples**: Check `IMPROVEMENTS.md` for detailed examples
- **Issues**: File issues on GitHub
- **Community**: Join Agno Discord

## Rollback Plan

If you need to rollback:

1. Restore old code from git:
   ```bash
   git checkout <previous-commit>
   ```

2. Restore database backup:
   ```bash
   cp data/jee_student.db.backup data/jee_student.db
   ```

3. Downgrade Agno:
   ```bash
   pip install agno==1.x.x
   ```

## Next Steps

After migration:

1. ✅ Test with a single student
2. ✅ Test with multiple students (verify isolation)
3. ✅ Test session continuations
4. ✅ Verify structured outputs are working
5. ✅ Check memory persistence
6. ✅ Monitor performance

Then explore advanced features:
- Workflows for deterministic study sessions
- Reasoning tools for better decision-making
- Knowledge tools for smarter RAG
- Monitoring and metrics

Happy learning! 🎓
