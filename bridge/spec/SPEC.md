# Agent Bridge Protocol v1 (ABP v1)

> A lightweight, transport-agnostic protocol for AI agents to communicate,
> collaborate, and learn from each other.

## 1. Goals

- **Zero dependency**: No client, no runtime, no framework required
- **Transport agnostic**: Same protocol works over files, HTTP, STDIO, MCP
- **Reliable**: Built-in ACK, TTL, and expiry mechanism
- **Interoperable**: Any agent can participate — Hermes, Claude Code, Codex, or a bash script

## 2. Message Format

```json
{
  "version": "abp/v1",
  "id": "msg_1780954000_a1b2",
  "from": "hermes",
  "to": "clawx",
  "type": "task",
  "payload": {},
  "timestamp": "2026-06-09T10:00:00Z",
  "reply_to": "",
  "expires_at": ""
}
```

### 2.1 Fields

| Field       | Type   | Required | Default | Description |
|-------------|--------|----------|---------|-------------|
| `version`   | string | yes      | —       | Always `"abp/v1"` |
| `id`        | string | yes      | —       | Unique ID: `msg_<unix_ms>_<4-char-random>` |
| `from`      | string | yes      | —       | Sender name. Lowercase, max 32 chars |
| `to`        | string | yes      | —       | `"*"` for broadcast, agent name for direct |
| `type`      | string | yes      | —       | See §2.2 |
| `payload`   | object | yes      | —       | Type-specific |
| `timestamp` | string | yes      | —       | ISO 8601 UTC |
| `reply_to`  | string | no       | `""`    | ID of the message this is responding to |
| `expires_at`| string | no       | none    | ISO 8601 UTC. Messages past this are ignored |

### 2.2 Message Types

| Type       | Direction     | Description |
|------------|---------------|-------------|
| `ping`     | any → any     | Liveness check. Payload: `{}` |
| `pong`     | any → any     | Ping response. Payload: `{}` |
| `task`     | any → any     | Request work from another agent |
| `result`   | any → any     | Response to a task. Includes `status`, `summary`, `output` |
| `context`  | any → any     | Share knowledge/state |
| `train`    | any → any     | Send training data or feedback for mutual improvement |
| `ack`      | any → any     | Acknowledgment. Must include `reply_to` with the original message ID |
| `error`    | any → any     | Error report. Includes `code` and `message` |
| `announce` | any → *       | Agent announcing its presence. Sent on connect |

## 3. Directory Structure (File Transport)

```
<bridge-dir>/
├── inbox/
│   └── <agent-name>/       ← Messages FOR this agent (others write here)
├── shared/                  ← Broadcast messages (to: "*")
├── .bridge.json             ← Peer registry
└── .archive/                ← Consumed messages (auto-managed)
```

**Key rule**: Agent A sends to Agent B → writes to `inbox/B/`. Agent B polls `inbox/B/`.

## 4. ACK Mechanism

Every message should be acknowledged. Two modes:

### 4.1 Auto-ACK (recommended)

When an agent polls and reads a message, it **automatically** sends an `ack` message back:

```json
{
  "version": "abp/v1",
  "id": "msg_1780954100_c3d4",
  "from": "clawx",
  "to": "hermes",
  "type": "ack",
  "payload": {},
  "timestamp": "2026-06-09T10:00:01Z",
  "reply_to": "msg_1780954000_a1b2"
}
```

### 4.2 Manual ACK

For task/result workflows, the `result` message acts as the acknowledgment.
The `reply_to` field links it back to the original task.

### 4.3 Retry & Timeout

| Field | Description |
|-------|-------------|
| `reply_to` | Links message to previous one in conversation |
| `expires_at` | Message TTL. Past this time → silently ignored |
| Auto-cleanup | Expired messages are deleted without processing |

## 5. Transports

### 5.1 File Transport

Write JSON files to `inbox/<target>/` or `shared/`. Read from your own `inbox/`.

```bash
# Send: write to recipient's inbox
echo '{"version":"abp/v1","id":"msg_xxx","from":"hermes","to":"clawx","type":"task","payload":{"goal":"hi"},"timestamp":"..."}' > ~/.agent-bridge/inbox/clawx/msg_xxx.json

# Poll: read from your inbox
cat ~/.agent-bridge/inbox/hermes/*.json
```

Python API:
```python
from agent_bridge.bridge import send, poll_with_ack

send("clawx", "task", {"goal": "analyze data"})
messages = poll_with_ack()  # auto-ACKs received messages
```

CLI:
```bash
file_bridge.py send clawx task '{"goal":"analyze data"}'
file_bridge.py poll
file_bridge.py listen
```

### 5.2 HTTP Transport

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/msg` | Send a message |
| `GET`  | `/inbox/<agent>` | Poll for messages (returns + auto-ACKs) |
| `GET`  | `/peers` | List connected agents |
| `POST` | `/ack/<msg-id>` | Manually acknowledge a message |

### 5.3 MCP Transport

MCP-compatible agents (Claude Code, Hermes, Cursor) can use ABP natively.

**For Hermes** — add to `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  abp:
    command: "python"
    args: ["-m", "agent_bridge.mcp_server"]
```

**For Claude Code** — start the server alongside Claude Code:
```bash
# Terminal 1: start MCP server
python -m agent_bridge.mcp_server

# Terminal 2: Claude Code
claude
```

### 5.4 STDIO Transport

Each line is a JSON message. Best for chained CLI tools.

```
Agent A → Agent B (pipe):
{"version":"abp/v1","id":"msg_1","from":"a","to":"b","type":"task","payload":{},"timestamp":"..."}
Agent B → Agent A (stdout):
{"version":"abp/v1","id":"msg_2","from":"b","to":"a","type":"result","payload":{"status":"ok"},"timestamp":"...","reply_to":"msg_1"}
```

## 6. Peer Discovery

Agents register in `.bridge.json`:

```json
{
  "peers": {
    "hermes": {
      "last_seen": "2026-06-09T10:00:00Z",
      "capabilities": ["skills", "memory", "code"],
      "transport": ["file"]
    }
  },
  "bridge_version": "abp/v1",
  "version_support": ["abp/v1"]
}
```

New agents send `announce` → other agents see them in the peer list.

## 7. End-to-End Flow

```
Hermes                          Bridge                          ClawX
  |                               |                               |
  |--[announce]----------------->|   <--[announce]----------------|
  |                               |                               |
  |--[task: analyze stocks]----->|  write to inbox/clawx/        |
  |                               |                               |
  |                               |  poll → reads task            |
  |                               |  auto-ACK back to Hermes      |
  |<- [ack] ---------------------|                               |
  |                               |  [processes task]             |
  |                               |  writes result to inbox/hermes|
  |<- [result: 5 picks] ---------|                               |
  |                               |                               |
```

## 8. Error Handling

| Code | Meaning |
|------|---------|
| `UNKNOWN_TYPE` | Message type not recognized |
| `INVALID_PAYLOAD` | Payload doesn't match schema |
| `MESSAGE_EXPIRED` | `expires_at` is in the past |
| `HANDLER_ERROR` | Agent's message handler failed |
| `TIMEOUT` | Task took too long |

## 9. Security

- ABP is designed for **trusted environments** (localhost, VPN, private network)
- Use TLS for HTTP transport in production
- Set directory permissions to `700` on shared machines
- Validate all incoming messages against §2 schema

## 10. Versioning

- Current: `abp/v1`
- Backward compatible: new fields, new message types
- Breaking: new major version (`abp/v2`)
- Unknown fields MUST be ignored (forward compatible)

## 11. Implementation Checklist

- [ ] Can generate valid `abp/v1` messages with unique IDs
- [ ] Implements at least one transport
- [ ] Responds to `ping` with `pong`
- [ ] **Auto-ACKs received messages** (or implements manual ack)
- [ ] **Checks `expires_at`** and ignores expired messages
- [ ] Removes consumed messages (file transport)
- [ ] Announces presence on connect
- [ ] Validates incoming messages before processing
- [ ] `.bridge.json` accurately reflects the transport in use
