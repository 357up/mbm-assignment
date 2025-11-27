#!/usr/bin/env python3
"""Compatibility wrapper for Helm invocations from ansible helm module."""
from __future__ import annotations

import os
import shutil
import sys


def resolve_target() -> str:
    """Resolve the underlying Helm binary path."""
    env_target = os.environ.get("HELM_WRAPPER_TARGET")
    if env_target:
        return env_target
    target = shutil.which("helm")
    if target:
        return target
    raise SystemExit("Unable to locate Helm binary for wrapper execution")


def main() -> None:
    target = resolve_target()
    filtered_args = [arg for arg in sys.argv[1:] if arg != "--all"]
    os.execvp(target, [target, *filtered_args])


if __name__ == "__main__":
    main()
