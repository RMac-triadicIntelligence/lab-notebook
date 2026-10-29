"""Agent subprocess entry (hardened mode).

Reads one init line {"stub":..., "obs":...} from stdin, then runs the named stub with a
PipeHandle that talks to the parent over stdin/stdout. This process holds no world objects;
its only influence on shared state is the messages it sends, which the parent validates.
Stdout carries only the protocol; diagnostics go to stderr.
"""
import json
import sys

import agents
from handle import PipeHandle


def main():
    init = json.loads(sys.stdin.readline())
    stub = agents.REGISTRY[init["stub"]]
    obs = init["obs"]
    h = PipeHandle(sys.stdin, sys.stdout)
    try:
        stub(h, obs)
        if not h.done:
            h.report("ended", None)
    except Exception as e:  # a bypass attempt that reached a missing ref lands here
        try:
            sys.stdout.write(json.dumps({"a": "crash", "err": type(e).__name__}) + "\n")
            sys.stdout.flush()
        except Exception:
            pass


if __name__ == "__main__":
    main()
