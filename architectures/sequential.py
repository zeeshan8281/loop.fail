"""sequential — agents run in order, each receives the previous one's output.

The loop wraps the whole chain: if the verifier rejects, the chain runs again
with the verifier's feedback prepended. Bounded by the kill switch in ctx.
"""
from loop_io import extract_files


def run(ctx):
    feedback = ""
    while ctx.should_continue():
        msg = ctx.context_blob()
        if feedback:
            msg += f"\n\n--- VERIFIER FEEDBACK (last attempt failed) ---\n{feedback}"
        out = ""
        for i in range(len(ctx.agents)):
            out = ctx.agent(i, msg + (f"\n\n--- PREVIOUS AGENT ---\n{out}" if out else ""))
        passed, feedback = ctx.verify(extract_files(out))
        if passed:
            return
