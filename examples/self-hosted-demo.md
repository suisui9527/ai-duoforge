# AI Pair — Self-Hosted Demo

This example shows how to run AI Pair with two terminal windows on your own machine.

## Requirements

- Two AI agents that can read/write files (Hermes, Claude Code, Codex, ChatGPT with file access)
- Python 3.8+

## Setup

```bash
# Create a demo project
mkdir ai-pair-demo && cd ai-pair-demo
duoforge init coding

# You'll see:
# ✓ AI Pair initialized for: coding
#   Directory: /path/to/ai-pair-demo
#   Pair: Senior Software Architect... ↔ focused implementer...

tree -a
# .ai-pair/
# ├── session.json         # Config
# ├── overseer_prompt.md   # Role definition
# ├── worker_prompt.md     # Role definition
# ├── inbox/               # Overseer reads from here
# └── outbox/              # Worker reads from here
```

## Message Format

Tasks and results use this JSON format:

```json
// Task (from Overseer to Worker)
{
  "version": "ai-pair/v1",
  "type": "task",
  "id": "task_001",
  "from": "overseer",
  "to": "worker",
  "payload": {
    "goal": "Create a FastAPI endpoint GET /hello",
    "acceptance": [
      "Returns {\"message\": \"Hello World\"}",
      "Includes status code 200",
      "Has a unit test"
    ]
  },
  "timestamp": "2026-06-09T00:00:00Z"
}

// Result (from Worker back to Overseer)
{
  "version": "ai-pair/v1",
  "type": "result",
  "id": "result_001",
  "in_response_to": "task_001",
  "from": "worker",
  "to": "overseer",
  "payload": {
    "status": "done",
    "files": ["main.py", "test_main.py"],
    "summary": "Created endpoint with test. All passing."
  },
  "timestamp": "2026-06-09T00:01:00Z"
}

// Revision (Overseer sends back)
{
  "version": "ai-pair/v1",
  "type": "task",
  "id": "task_001_v2",
  "in_response_to": "task_001",
  "from": "overseer",
  "to": "worker",
  "payload": {
    "goal": "Fix error handling on GET /hello",
    "acceptance": [
      "Returns 404 if name is empty",
      "Returns 400 if name contains special chars"
    ],
    "feedback": "Need input validation before returning"
  },
  "timestamp": "2026-06-09T00:02:00Z"
}
```

## Watching the Loop

```bash
# Terminal 1: Watch the communication
watch -n 2 'ls -la .ai-pair/inbox/ .ai-pair/outbox/'

# Terminal 2: See the output files
watch -n 2 'cat .ai-pair/outbox/task_001.json 2>/dev/null || echo "Waiting..."'
```
