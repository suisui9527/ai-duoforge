# Demo: Two agents chatting through ABP bridge

This example shows a conversation between `agent-alpha` and `agent-beta`
using the Agent Bridge Protocol file transport.

## Setup

```bash
# Terminal 1: Agent Alpha
export ABP_BRIDGE_DIR="/tmp/abp-demo"
export ABP_AGENT_NAME="agent-alpha"
python3 -m agent_bridge.mcp_server announce '["demo"]'

# Terminal 2: Agent Beta
export ABP_BRIDGE_DIR="/tmp/abp-demo"
export ABP_AGENT_NAME="agent-beta"
python3 -m agent_bridge.mcp_server announce '["demo"]'
```

## Conversation

```
Alpha:  "Hey Beta, can you process this data?"
         → send a task message to agent-beta

Beta:   (polls, reads the task)
        "Sure, I'll get right on it."
        → send result back to agent-alpha

Alpha:  (polls, gets the result)
        "Thanks! Here's some context for next time."
        → send context to agent-beta
```

## Commands cheat sheet

```bash
# Send a task
python -m agent_bridge.mcp_server send agent-beta task \
  '{"goal":"analyze this CSV file","context":"/tmp/data.csv"}'

# Check messages
python -m agent_bridge.mcp_server poll

# Share context
python -m agent_bridge.mcp_server send agent-alpha context \
  '{"topics":["market"],"data":{"status":"bullish"}}'

# Training feedback
python -m agent_bridge.mcp_server send agent-beta train \
  '{"domain":"trading","observations":["factor X works better in cold market"]}'

# See who's online
python -m agent_bridge.mcp_server peers
```
