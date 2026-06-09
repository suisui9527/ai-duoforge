#!/usr/bin/env python3
"""
Agent Bridge Protocol v1 - File Transport CLI

Standalone CLI for ABP file transport. Zero dependencies beyond Python 3.6+.

Usage:
    export ABP_BRIDGE_DIR="$HOME/.agent-bridge"
    export ABP_AGENT_NAME="my-agent"

    file_bridge.py send clawx task '{"goal":"hello"}'
    file_bridge.py poll
    file_bridge.py listen
    file_bridge.py announce '["code","web"]'
"""

import json
import os
import sys
import time
import threading
from pathlib import Path

# Try importing the package, fallback to inline implementation
try:
    from agent_bridge.bridge import (BRIDGE_DIR, ABP_AGENT, send, poll,
                                      poll_with_ack, peers, announce,
                                      new_id, timestamp, make_message, validate)
except ImportError:
    # Inline minimal implementation
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from agent_bridge.bridge import (BRIDGE_DIR, ABP_AGENT, send, poll,
                                      poll_with_ack, peers, announce,
                                      new_id, timestamp, make_message, validate)


class FileBridge:
    """File-based ABP transport with background listener."""

    def __init__(self, bridge_dir: str = None, agent_name: str = None,
                 poll_interval: float = 2.0):
        self.bridge_dir = Path(bridge_dir or os.environ.get(
            "ABP_BRIDGE_DIR", os.path.expanduser("~/.agent-bridge")))
        self.agent_name = agent_name or os.environ.get("ABP_AGENT_NAME", "cli")
        self.poll_interval = poll_interval
        self._running = False
        self._handlers = {}

    def send(self, to: str, msg_type: str, payload: dict,
             reply_to: str = "", expires_in_s: int = 0) -> dict:
        return send(to, msg_type, payload, reply_to, expires_in_s)

    def poll(self) -> list[dict]:
        return poll_with_ack(self.agent_name)

    def peers(self) -> dict:
        return peers()

    def announce(self, capabilities: list[str] = None):
        return announce(capabilities)

    def on(self, msg_type: str, handler):
        self._handlers[msg_type] = handler

    def _loop(self):
        while self._running:
            for msg in self.poll():
                if msg["type"] == "ping":
                    self.send(msg["from"], "pong", {})
                handler = self._handlers.get(msg["type"])
                if handler:
                    try:
                        handler(msg)
                    except Exception as e:
                        self.send(msg["from"], "error",
                                  {"code": "HANDLER_ERROR", "message": str(e),
                                   "reply_to": msg["id"]})
            time.sleep(self.poll_interval)

    def start(self, daemon: bool = True):
        self._running = True
        self.announce()
        t = threading.Thread(target=self._loop, daemon=daemon)
        t.start()

    def stop(self):
        self._running = False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ABP File Transport")
    parser.add_argument("--dir", default=str(BRIDGE_DIR),
                        help=f"Bridge dir (default: {BRIDGE_DIR})")
    parser.add_argument("--agent", default=ABP_AGENT,
                        help=f"Agent name (default: {ABP_AGENT})")

    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("send", help="Send a message")
    sp.add_argument("to")
    sp.add_argument("type")
    sp.add_argument("payload", nargs="+")

    sub.add_parser("poll", help="Poll for messages")
    sub.add_parser("peers", help="List agents")
    sub.add_parser("listen", help="Continuously listen")

    ap = sub.add_parser("announce", help="Announce presence")
    ap.add_argument("capabilities", nargs="?", default="[]")

    args = parser.parse_args()

    os.environ["ABP_BRIDGE_DIR"] = args.dir
    os.environ["ABP_AGENT_NAME"] = args.agent

    if args.command == "send":
        payload = json.loads(" ".join(args.payload))
        msg = send(args.to, args.type, payload)
        print(json.dumps(msg, indent=2))

    elif args.command == "poll":
        msgs = poll_with_ack()
        print(json.dumps(msgs, indent=2) if msgs else "[]")

    elif args.command == "peers":
        p = peers()
        print(json.dumps(p, indent=2) if p else "No peers")

    elif args.command == "announce":
        caps = json.loads(args.capabilities)
        announce(caps)
        print(json.dumps({"status": "announced", "agent": args.agent}))

    elif args.command == "listen":
        bridge = FileBridge(args.dir, args.agent)
        print(f"[ABP] Agent '{args.agent}' listening on {args.dir}", file=sys.stderr)
        try:
            bridge.start(daemon=False)
            while bridge._running:
                time.sleep(1)
        except KeyboardInterrupt:
            bridge.stop()
            print("\n[ABP] Stopped", file=sys.stderr)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
