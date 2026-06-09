#!/usr/bin/env bash
# Agent Bridge CLI - Zero-dependency shell client
# Usage: source abp.sh  (loads functions)
# Or:    bash abp.sh <command> [args...]

ABP_DIR="${ABP_BRIDGE_DIR:-$HOME/.agent-bridge}"
ABP_AGENT="${ABP_AGENT_NAME:-cli}"

# ── Helpers ──────────────────────────────────────────────────────────────────

_abp_id() {
    echo "msg_$(date +%s%3N)_$(dd if=/dev/urandom bs=4 count=1 2>/dev/null | xxd -p | head -c 4 || echo "abcd")"
}

_abp_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

_abp_msg() {
    local to="$1" type="$2" payload="$3" reply_to="${4:-}"
    local id
    id=$(_abp_id)
    local ts
    ts=$(_abp_ts)
    cat <<EOF
{
  "version": "abp/v1",
  "id": "$id",
  "from": "$ABP_AGENT",
  "to": "$to",
  "type": "$type",
  "payload": $payload,
  "timestamp": "$ts"
}
EOF
}

# ── Commands ─────────────────────────────────────────────────────────────────

abp_send() {
    local to="$1" type="$2" payload="$3"
    local msg
    msg=$(_abp_msg "$to" "$type" "$payload")
    local target_dir

    if [ "$to" = "*" ]; then
        target_dir="$ABP_DIR/shared"
    else
        target_dir="$ABP_DIR/outbox/$to"
    fi

    mkdir -p "$target_dir"
    local msg_id
    msg_id=$(echo "$msg" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    echo "$msg" > "$target_dir/$msg_id.json"
    echo "$msg"
}

abp_poll() {
    local inbox="$ABP_DIR/inbox/$ABP_AGENT"
    local shared="$ABP_DIR/shared"
    local archive="$ABP_DIR/.archive"

    mkdir -p "$archive"
    local found=0

    # Poll inbox
    if [ -d "$inbox" ]; then
        for f in "$inbox"/*.json; do
            [ -f "$f" ] || continue
            found=1
            cat "$f"
            echo "---"
            mv "$f" "$archive/" 2>/dev/null || rm -f "$f"
        done
    fi

    # Poll shared (skip our own messages)
    if [ -d "$shared" ]; then
        for f in "$shared"/*.json; do
            [ -f "$f" ] || continue
            local sender
            sender=$(python3 -c "import json; print(json.load(open('$f'))['from'])" 2>/dev/null)
            [ "$sender" = "$ABP_AGENT" ] && continue
            found=1
            cat "$f"
            echo "---"
            mv "$f" "$archive/" 2>/dev/null || rm -f "$f"
        done
    fi

    [ "$found" = "0" ] && echo ""
}

abp_listen() {
    echo "[ABP] Agent '$ABP_AGENT' listening on $ABP_DIR" >&2
    echo "[ABP] Press Ctrl+C to stop" >&2
    while true; do
        local msgs
        msgs=$(abp_poll)
        if [ -n "$msgs" ]; then
            echo "$msgs"
        fi
        sleep 2
    done
}

abp_peers() {
    local meta="$ABP_DIR/.bridge.json"
    if [ -f "$meta" ]; then
        cat "$meta"
    else
        echo '{"peers":{},"bridge_version":"abp/v1"}'
    fi
}

abp_announce() {
    local caps="${1:-[]}"
    mkdir -p "$ABP_DIR"
    abp_send "*" "announce" "{\"capabilities\":$caps,\"version\":\"1.0.0\",\"transport\":[\"file\"]}" > /dev/null

    # Update .bridge.json
    local meta="$ABP_DIR/.bridge.json"
    local existing="{}"
    [ -f "$meta" ] && existing=$(cat "$meta")
    python3 -c "
import json, sys
meta = json.loads('''$existing'''.replace(\"'\", '\"'))
peers = meta.get('peers', {})
peers['$ABP_AGENT'] = {
    'last_seen': '$(_abp_ts)',
    'capabilities': $caps,
    'transport': ['file']
}
meta['peers'] = peers
meta['bridge_version'] = 'abp/v1'
with open('$meta', 'w') as f:
    json.dump(meta, f, indent=2)
" 2>/dev/null
    echo "[ABP] Announced: $ABP_AGENT"
}

# ── Main ─────────────────────────────────────────────────────────────────────

case "${1:-}" in
    send)
        shift
        abp_send "$@"
        ;;
    poll)
        abp_poll
        ;;
    listen)
        abp_listen
        ;;
    peers)
        abp_peers
        ;;
    announce)
        shift
        abp_announce "${1:-[]}"
        ;;
    help|--help|-h)
        cat <<HELP
Agent Bridge Protocol v1 — CLI Client

Usage:
  abp.sh send <to> <type> '<json-payload>'    Send a message
  abp.sh poll                                   Check for new messages
  abp.sh listen                                 Continuously listen for messages
  abp.sh peers                                  List connected agents
  abp.sh announce '["cap1","cap2"]'             Announce presence

Environment:
  ABP_BRIDGE_DIR    Bridge directory (default: ~/.agent-bridge)
  ABP_AGENT_NAME    Your agent name (default: cli)

Examples:
  ABP_AGENT_NAME=my-script bash abp.sh send "*" announce '["data","monitor"]'
  bash abp.sh send clawx task '{"goal":"hello"}'
  bash abp.sh poll | python3 -m json.tool
HELP
        ;;
    *)
        echo "Usage: bash abp.sh <command> [args]"
        echo "Commands: send, poll, listen, peers, announce, help"
        ;;
esac
