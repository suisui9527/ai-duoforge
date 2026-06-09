#!/usr/bin/env python3
"""DuoForge CLI — Initialize and run dual-agent collaboration sessions."""

import argparse
import json
import os
import subprocess
import sys
import time
import yaml
from pathlib import Path

CONFIGS_DIR = Path(__file__).resolve().parent.parent / "configs"

AVAILABLE_DOMAINS = {}

def _load_domains():
    if not CONFIGS_DIR.exists():
        return
    for f in sorted(CONFIGS_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text())
            name = data.get("domain", f.stem)
            desc = data.get("description", "")
            AVAILABLE_DOMAINS[name] = {"file": f.name, "description": desc}
        except Exception:
            pass

def cmd_init(args):
    """Initialize an AI Pair session for a given domain."""
    domain = args.domain
    target_dir = Path(args.dir).resolve() if args.dir else Path.cwd()
    
    # Load domain config
    config_file = CONFIGS_DIR / f"{domain}.yaml"
    if not config_file.exists():
        print(f"✗ Domain '{domain}' not found.")
        print(f"  Available domains: {', '.join(AVAILABLE_DOMAINS.keys())}")
        sys.exit(1)
    
    config = yaml.safe_load(config_file.read_text())
    
    # Create .ai-pair directory in target
    pair_dir = target_dir / ".ai-pair"
    pair_dir.mkdir(parents=True, exist_ok=True)
    
    # Write session config
    session_config = {
        "version": "ai-pair/v1",
        "domain": domain,
        "created_at": time.time(),
        "status": "initialized",
        "config": config,
    }
    (pair_dir / "session.json").write_text(json.dumps(session_config, indent=2, ensure_ascii=False))
    
    # Create inbox/outbox for agent communication
    (pair_dir / "inbox").mkdir(exist_ok=True)
    (pair_dir / "outbox").mkdir(exist_ok=True)
    
    # Write agent prompt files
    for role in ["overseer", "worker"]:
        prompt = config.get("pair", {}).get(role, {}).get("persona", "")
        (pair_dir / f"{role}_prompt.md").write_text(prompt)
    
    print(f"✓ AI DuoForge initialized for: {domain}")
    print(f"  Directory: {target_dir}")
    print(f"  Pair: {config.get('pair', {}).get('overseer', {}).get('persona', 'Overseer')[:40]}...")
    print(f"      ↔ {config.get('pair', {}).get('worker', {}).get('persona', 'Worker')[:40]}...")
    print()
    print("  Next: open this directory in your overseer agent and run:")
    print(f"    cat .ai-pair/overseer_prompt.md")
    print()
    print("  Then open the worker agent in the same directory.")
    print("  They will communicate through .ai-pair/inbox/ and .ai-pair/outbox/")


def cmd_list(args):
    """List available domains."""
    _load_domains()
    if not AVAILABLE_DOMAINS:
        print("No domain configs found.")
        return
    
    print(f"\n{'Domain':<20} {'Description':<50}")
    print("-" * 70)
    for name, info in sorted(AVAILABLE_DOMAINS.items()):
        desc = info["description"][:48]
        print(f"{name:<20} {desc:<50}")
    print()


def cmd_inspect(args):
    """Show details of a domain config."""
    _load_domains()
    domain = args.domain
    
    config_file = CONFIGS_DIR / f"{domain}.yaml"
    if not config_file.exists():
        print(f"✗ Domain '{domain}' not found.")
        return
    
    config = yaml.safe_load(config_file.read_text())
    print(f"\n=== {domain} ===\n")
    print(f"Description: {config.get('description', 'N/A')}")
    print(f"Quality gates: {json.dumps(config.get('quality_gates', []), indent=2)}")
    print()
    
    for role in ["overseer", "worker"]:
        role_data = config.get("pair", {}).get(role, {})
        print(f"--- {role.upper()} ---")
        print(f"Persona: {role_data.get('persona', 'N/A')[:100]}...")
        criteria = role_data.get("review_criteria", role_data.get("output_format"))
        if criteria:
            print(f"Criteria: {json.dumps(criteria, indent=2)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="AI DuoForge — Dual-agent collaboration framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")
    
    # init
    p_init = sub.add_parser("init", help="Initialize a pair session")
    p_init.add_argument("domain", help="Domain type (coding, writing, analysis, ...)")
    p_init.add_argument("-d", "--dir", help="Target project directory (default: current)")
    
    # list
    sub.add_parser("list", help="List available domains")
    
    # inspect
    p_inspect = sub.add_parser("inspect", help="Show domain config details")
    p_inspect.add_argument("domain", help="Domain to inspect")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    _load_domains()
    
    if args.command == "init":
        cmd_init(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "inspect":
        cmd_inspect(args)


if __name__ == "__main__":
    main()
