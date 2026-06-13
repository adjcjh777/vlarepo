#!/usr/bin/env python3
"""Compatibility hook entrypoint for tools that prefer a Python script path."""

from agent_bus.hooks import main


if __name__ == "__main__":
    raise SystemExit(main())
