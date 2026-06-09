# AI DuoForge — Dual-Agent Collaboration Framework

> Two AI agents working together beat one.
> An overseer + worker pair iterating faster than any solo agent.

**AI DuoForge** is an open-source framework where two AI agents collaborate in an Overseer+Worker loop. One plans and reviews (Overseer), the other executes (Worker). They iterate automatically until quality passes. You just ship the result.

```ascii
┌──────────┐          ┌──────────┐          ┌──────────┐
│   User   │──task──►│ Overseer │──task──►│  Worker  │
│ (You)    │          │ (Plan +  │          │ (Execute)│
│          │◄─result─│  Review) │◄─result─│          │
└──────────┘          └──────────┘          └──────────┘
```

---

## Why DuoForge?

| Solo Agent | AI DuoForge |
|------------|-------------|
| Plans AND codes in one head → loses context switching | Overseer focuses on plan, Worker focuses on execution |
| Self-review is weak (confirmation bias) | Independent reviewer catches mistakes |
| One model's blind spots persist | Two different agents cover each other's gaps |
| Hits token limits on big tasks | Split across two contexts = 2× effective capacity |

---

## Use Anywhere

| Domain | Overseer does | Worker does |
|--------|--------------|-------------|
| **Coding** | Architecture, code review | Write code, fix bugs |
| **Writing** | Outline, tone check | Draft, revise |
| **Translation** | Glossary, QA | Translate |
| **Data Analysis** | Methodology, validation | Query, chart |
| **Stock Analysis** | Strategy, risk review | Fetch quotes, compute |
| **Research** | Question, source check | Gather, summarize |

---

## Quick Start

```bash
# Install
pip install ai-duoforge

# Init a pair for your domain
duoforge init coding -d ./my-project

# Then open Overseer and Worker agents in that directory.
# They auto-discover each other via .ai-pair/inbox/ and .ai-pair/outbox/
```

### Supported Agent Pairs

| Overseer | Worker | Transport |
|----------|--------|-----------|
| Hermes Agent | Claude Code | MCP / File bridge |
| Hermes Agent | Codex CLI | File bridge |
| Claude Code | Codex CLI | File bridge |
| Any AI | Any AI | File / HTTP / STDIO |

---

## How It Works

1. **You give a requirement**
2. **Overseer** breaks it into tasks with acceptance criteria
3. **Worker** executes, returns result
4. **Overseer** reviews — if it fails, sends back with feedback
5. **Loop until pass** → you get the deliverable

---

## Architecture

```
                    ┌─────────────────────┐
                    │   AI DuoForge CLI   │
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

---

## License

MIT — Free for any use, commercial or personal.

---

## 中文简介

**AI DuoForge（双AI协作框架）** — 两个AI组成监工+工人编队，自动迭代直到质量达标。

你只做两件事：**提需求 + 验收结果**。中间全自动。

支持场景：写代码、写文章、翻译、数据分析、股票分析、研究……
