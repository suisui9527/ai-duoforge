# AI Pair Quickstart

This example walks through setting up an AI Pair for a coding project.

## Step 1: Install

```bash
pip install ai-duoforge
# or clone and run locally
git clone https://github.com/suisui9527/ai-duoforge
cd ai-duoforge
pip install -e .
```

## Step 2: Init

```bash
mkdir my-api && cd my-api
duoforge init coding
```

## Step 3: Open Overseer

Tell your Overseer agent (e.g., Hermes, Claude Code):

```
I'm the OVERSEER in an AI Pair session.
Read .ai-pair/overseer_prompt.md for my role.
Check .ai-pair/session.json for context.
My worker is at .ai-pair/worker/ — send tasks via .ai-pair/outbox/.
```

The Overseer will:
1. Read `.ai-pair/overseer_prompt.md`
2. Break down the project into tasks
3. Write `task_001.json` to `.ai-pair/outbox/`
4. Wait for Worker to write `result_001.json` to `.ai-pair/inbox/`
5. Review the result and either accept or send back for fixes

## Step 4: Open Worker

Tell your Worker agent (e.g., Claude Code, Codex):

```
I'm the WORKER in an AI Pair session.
Read .ai-pair/worker_prompt.md for my role.
My overseer sends tasks to .ai-pair/inbox/.
I write results to .ai-pair/outbox/.
Poll every 30 seconds for new tasks.
```

The Worker will:
1. Read `.ai-pair/worker_prompt.md`
2. Poll `.ai-pair/inbox/` for tasks
3. Execute each task
4. Write `result_001.json` to `.ai-pair/outbox/`
5. Wait for next task or acceptance

## Step 5: Iterate

The pair loops:
```
Overseer: task_001.json → Worker
Worker:  result_001.json → Overseer
Overseer: "Fix the error handling" → Worker (revision)
Worker:  result_001_v2.json → Overseer
Overseer: "Accepted. Here's task_002..."
```

## Step 6: Done

When all tasks pass review, Overseer delivers the summary.
You get a PR, document, or whatever you asked for.

---

## Other Domains

```bash
duoforge init writing     # Article/document writing pair
duoforge init translation # Translation QA pair
duoforge init analysis    # Data analysis pair
duoforge init research    # Research pair
duoforge list             # See all domains
duoforge inspect coding   # See config details
```
