<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/AI_DuoForge-000000?style=for-the-badge&logo=github&logoColor=white">
    <img alt="AI DuoForge" src="https://img.shields.io/badge/AI_DuoForge-000000?style=for-the-badge&logo=github&logoColor=white">
  </picture>
</p>

<p align="center">
  <em>Two AI agents working together beat one.</em><br>
  <strong>Overseer plans & reviews · Worker executes · They iterate until quality passes</strong>
</p>

<p align="center">
  <a href="#quick-start"><strong>Quick Start</strong></a> ·
  <a href="#how-it-works"><strong>How It Works</strong></a> ·
  <a href="#use-cases"><strong>Use Cases</strong></a> ·
  <a href="#agent-bridge-protocol"><strong>Protocol</strong></a> ·
  <a href="#configuration"><strong>Config</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/suisui9527/ai-duoforge/ci.yml?style=flat-square&logo=github&label=CI" alt="CI">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT">
  <img src="https://img.shields.io/badge/status-alpha-orange?style=flat-square" alt="Alpha">
</p>

---

## Why DuoForge?

A solo AI agent has one brain. It plans, codes, reviews — all in the same context window. Confirmation bias kicks in. Token limits hit. Blind spots compound.

**DuoForge splits the mind.**

One agent **oversees** — designs the architecture, splits work into tasks, reviews output. The other **executes** — writes code, runs analysis, produces drafts. They iterate in a tight loop until the overseer signs off. You just ship.

| Solo Agent | AI DuoForge |
|---|---|
| Plans AND codes in one head → context thrashing | Overseer focuses on plan, Worker on execution |
| Self-review is weak (confirmation bias) | Independent reviewer catches mistakes |
| One model's blind spots persist | Two agents cover each other's gaps |
| Hits token limits on large tasks | Split across two contexts = 2× effective capacity |

This isn't a new protocol. It's a **role separation** pattern that works with any AI agent — Hermes, Claude Code, Codex, ChatGPT, or even a bash script.

---

## Quick Start

```bash
# Install
pip install ai-duoforge
# or clone
git clone https://github.com/suisui9527/ai-duoforge.git
cd ai-duoforge
pip install -e .

# Initialize a pair session
duoforge init coding -d ./my-project

# See what's available
duoforge list
duoforge inspect coding
```

### Run Your First Pair

**1. Open Overseer** (Hermes, Claude Code, etc.) in the project directory:

```
I'm the OVERSEER in a DuoForge session.
Read .ai-pair/overseer_prompt.md for my role.
Check .ai-pair/session.json for context.
Send tasks via .ai-pair/outbox/ — I review and iterate.
```

**2. Open Worker** (Claude Code, Codex, etc.) in the same directory:

```
I'm the WORKER in a DuoForge session.
Read .ai-pair/worker_prompt.md for my role.
Poll .ai-pair/inbox/ for tasks — I execute and return results.
```

**3. Watch them iterate** as Overseer splits work, Worker executes, Overseer reviews, loops until done.

---

## How It Works

```
                    ┌─────────────────────┐
                    │    DuoForge CLI      │
                    │  duoforge init/start │
                    └─────────┬───────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ┌───────────────┐             ┌───────────────┐
      │   Overseer    │◄────JSON────│    Worker     │
      │  (Agent A)    │──messages──►│   (Agent B)   │
      └───────┬───────┘             └───────┬───────┘
              │                             │
              └───────────┬─────────────────┘
                          │
                  ┌───────┴───────┐
                  │ Agent Bridge  │
                  │ (File/HTTP)   │
                  └───────────────┘
```

The loop:

```
You         Overseer     Worker
 │             │            │
 ├─ requirement             │
 │             │            │
 │             ├─ task ────►│
 │             │            ├── execute
 │             │◄── result ─┤
 │             │            │
 │             ├─ review    │
 │     [fail]  ├─ task v2 ─►│
 │             │            ├── fix
 │             │◄── result ─┤
 │             │            │
 │   [pass]    │            │
 ◄── deliver ──┤            │
```

No server. No daemon. No dependencies beyond Python. Just JSON files in a shared directory.

---

## Use Cases

| Domain | Overseer | Worker | What You Get |
|---|---|---|---|
| **Coding** | Architect reviewing code | Implementer writing features | PR-ready code, tests pass |
| **Writing** | Editor defining outline | Writer drafting sections | Polished article |
| **Translation** | QA specialist checking accuracy | Translator producing drafts | Native-quality translation |
| **Data Analysis** | Data scientist designing methodology | Analyst running queries | Reproducible analysis |
| **Research** | Research director planning investigation | Assistant gathering sources | Synthesized findings |
| **Stock Analysis** | Strategist managing risk | Analyst computing metrics | Actionable picks |

```bash
duoforge init coding        # Build a feature
duoforge init writing       # Draft a blog post
duoforge init analysis      # Analyze a dataset
duoforge init translation   # Localize content
duoforge init research      # Deep-dive a topic
```

Each domain comes with pre-built personas and quality gates. Customize them in `configs/<domain>.yaml`.

---

## Agent Bridge Protocol

Under the hood, agents communicate via **Agent Bridge Protocol v1 (ABP)** — a lightweight, transport-agnostic message format.

```json
{
  "version": "abp/v1",
  "id": "msg_1780954000_a1b2",
  "from": "hermes",
  "to": "clawx",
  "type": "task",
  "payload": { "goal": "implement GET /hello endpoint" },
  "timestamp": "2026-06-09T10:00:00Z"
}
```

### Message Types

| Type | Purpose | Example |
|---|---|---|
| `task` | Request work | "Implement feature X" |
| `result` | Return output | "Done, tests pass" |
| `ack` | Acknowledge receipt | "Got it" |
| `ping/pong` | Liveness check | Heartbeat |
| `context` | Share knowledge | "Market temp is 35" |
| `train` | Send feedback | "Factor X works better cold" |
| `announce` | Register presence | "Hermes online" |

### Transports

- **File** — Zero deps, JSON files in a shared directory
- **HTTP** — REST endpoints for remote agents
- **MCP** — Native integration (Hermes, Claude Code)
- **STDIO** — Pipe-friendly, chained CLI tools
- **Shell** — 100-line bash client (`bridge/implementations/cli/abp.sh`)

```bash
# Send a task via shell
export ABP_AGENT_NAME="hermes"
bash bridge/implementations/cli/abp.sh send clawx task \
  '{"goal":"analyze this data"}'

# Poll for results
bash bridge/implementations/cli/abp.sh poll
```

---

## Configuration

### Domain Configs

Each domain is a YAML file with roles, personas, and quality gates:

```yaml
# configs/coding.yaml
domain: coding
description: "Write, test, and review code"

quality_gates:
  - "No syntax errors"
  - "Tests pass (pytest or equivalent)"
  - "No security vulnerabilities"

pair:
  overseer:
    persona: >
      You are a Senior Software Architect. You split requirements
      into clear tasks. You review for correctness, test coverage,
      and style. You NEVER write code — you delegate.
    review_criteria:
      - "All tests pass"
      - "No obvious bugs or edge cases missed"

  worker:
    persona: >
      You are a focused implementer. You receive one task at a time,
      write clean code, add tests, return results. You do NOT redesign
      — you implement.
    output_format: "Working code + tests. Return diff or file list."
```

### Add Custom Domains

```bash
cp configs/coding.yaml configs/my-domain.yaml
# Edit the file, change domain name, personas, gates
duoforge list  # Now shows your custom domain
```

---

## Supported Agent Pairs

| Overseer | Worker | Best For |
|---|---|---|
| Hermes Agent | Claude Code | Complex coding projects |
| Hermes Agent | Codex CLI | Quick prototyping |
| Hermes Agent | ClawX | Quant/analysis workflows |
| Claude Code | Codex CLI | Heavy engineering |
| Any AI | Any AI | Whatever you dream up |

---

## Development

```bash
git clone https://github.com/suisui9527/ai-duoforge.git
cd ai-duoforge
pip install -e .

# Run the CLI
duoforge list
duoforge inspect coding
```

### Project Structure

```
ai-duoforge/
├── duoforge/                     # Python CLI
│   ├── __init__.py
│   └── cli.py                    # init, list, inspect commands
├── configs/                      # Domain configurations
│   ├── coding.yaml
│   ├── analysis.yaml
│   ├── writing.yaml
│   ├── translation.yaml
│   └── research.yaml
├── bridge/                       # Agent Bridge Protocol
│   ├── spec/SPEC.md              # Full protocol specification
│   └── implementations/
│       ├── file-bridge/          # Python file transport CLI
│       ├── cli/abp.sh            # Zero-dep shell client
│       └── hermes-skill/         # Hermes Agent integration
├── examples/                     # Guides and tutorials
│   ├── quickstart.md
│   ├── two-agent-chat.md
│   └── self-hosted-demo.md
├── .github/workflows/ci.yml      # CI pipeline
├── pyproject.toml                # Package config
└── README.md
```

---

## Roadmap

- [x] CLI: `init`, `list`, `inspect` commands
- [x] 5 domain configs with personas + quality gates
- [x] Agent Bridge Protocol v1 specification
- [x] File transport (Python + shell)
- [x] GitHub CI
- [ ] PyPI publish
- [ ] `duoforge start` — auto-launch both agents
- [ ] HTTP transport server
- [ ] MCP transport server
- [ ] Agent template marketplace
- [ ] Web dashboard for pair sessions

---

## License

MIT — Free for any use, commercial or personal.

---

<p align="center">
  Built by <a href="https://github.com/suisui9527">suisui9527</a> ·
  <a href="https://github.com/suisui9527/ai-duoforge/issues">Report Bug</a> ·
  <a href="https://github.com/suisui9527/ai-duoforge/discussions">Discussion</a>
</p>
