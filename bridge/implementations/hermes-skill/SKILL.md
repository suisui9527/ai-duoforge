---
name: agent-bridge
description: "Agent Bridge Protocol v1 — File transport. Connect Hermes with any other AI agent (ClawX, Claude Code, Codex, etc.) for task delegation, context sharing, and mutual learning."
version: 1.0.0
author: agent-bridge
platforms: [linux, macos, windows]
prerequisites:
  commands: [python3]
setup:
  help: "Set ABP_BRIDGE_DIR and ABP_AGENT_NAME env vars, or use defaults. The bridge auto-starts on first task."
---

# Agent Bridge — Hermes Skill

Connects Hermes to the Agent Bridge Protocol v1 network.
Enables task delegation, context sharing, and mutual training with other AI agents.

## How It Works

```
Other Agent (ClawX/Claude Code) ←→ [ABP Bridge] ←→ Hermes (you)
```

Messages are JSON files in a shared directory. No server, no daemon, no dependencies.

## Quick Start

### 1. Set up the bridge directory

```bash
export ABP_BRIDGE_DIR="$HOME/.agent-bridge"
export ABP_AGENT_NAME="hermes"
mkdir -p "$ABP_BRIDGE_DIR"/{inbox,outbox,shared,.archive}
```

### 2. Announce presence

Run once to register Hermes on the bridge:

```bash
python3 ~/agent-bridge/implementations/file-bridge/file_bridge.py \
  --dir "$ABP_BRIDGE_DIR" \
  --agent hermes \
  send "*" announce '{"capabilities":["skills","memory","web","code"],"version":"1.0.0","transport":["file"]}'
```

### 3. Verify peers

```bash
cat "$ABP_BRIDGE_DIR/.bridge.json"
```

If another agent is connected, you'll see both agents listed.

## Commands

### Send a task to another agent

```
I'm going to ask ClawX to screen these stocks
```

The bridge will:
1. Create a `task` message in the bridge directory
2. The other agent picks it up on its next poll
3. Result comes back to Hermes' inbox

### Check for new messages

```
Check the bridge
```

### Share context

```
Tell ClawX the current market temperature is 35
```

Sends a `context` type message.

### Send training feedback

```
Send ClawX my latest factor effectiveness data
```

Sends a `train` type message with observations.

## File Structure

```
$ABP_BRIDGE_DIR/
├── inbox/hermes/       ← Messages for Hermes
├── outbox/<agent>/     ← Messages for specific agents
├── shared/             ← Broadcast messages (*)
├── .archive/           ← Consumed messages
└── .bridge.json        ← Peer registry
```

## Use with Other Agents

### Claude Code

```bash
# Read latest message from Hermes
cat ~/.agent-bridge/inbox/claude-code/*.json 2>/dev/null

# Reply to Hermes
echo '{"version":"abp/v1","id":"msg_...","from":"claude-code","to":"hermes","type":"result","payload":{"status":"success","summary":"Done"}}' > ~/.agent-bridge/outbox/hermes/msg_reply.json
```

### Codex CLI

Same pattern as Claude Code — write JSON to the shared directory.

### Any Script

```bash
# Send message via curl to file system
curl -s -o /dev/null \
  -H "Content-Type: application/json" \
  -d '{"version":"abp/v1","id":"msg_1780954000_a1b2","from":"script","to":"hermes","type":"task","payload":{"goal":"check status"},"timestamp":"2026-06-09T10:00:00Z"}' \
  --data-binary @- \
  file://$ABP_BRIDGE_DIR/inbox/hermes/task.json
# But really just:
echo '{"version":"abp/v1","id":"msg_1780954000_a1b2","from":"script","to":"hermes","type":"task","payload":{"goal":"check status"},"timestamp":"2026-06-09T10:00:00Z"}' > "$ABP_BRIDGE_DIR/inbox/hermes/task.json"
```

## Cron: Auto-poll

If you want Hermes to automatically check the bridge:

```bash
hermes cron create \
  --name "agent-bridge-poll" \
  --schedule "every 1m" \
  --prompt "Check the Agent Bridge for new messages. If there are tasks, process them and reply." \
  --skills agent-bridge
```
