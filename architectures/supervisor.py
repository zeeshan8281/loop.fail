"""supervisor — the canonical Session 5 pattern.

agent[0] plans, the middle agents execute, agent[-1] audits. If the audit (or the
verifier) rejects, the workers run again with the feedback. Verify, don't trust.
"""
from loop_io import extract_files


def run(ctx):
    n = len(ctx.agents)
    feedback = ""
    while ctx.should_continue():
        plan = ctx.agent(0, ctx.context_blob() + tail(feedback))
        work = ""
        for i in range(1, n - 1):  # executors
            work = ctx.agent(i, f"{ctx.context_blob()}\n\n--- PLAN ---\n{plan}\n"
                                f"--- WORK SO FAR ---\n{work}{tail(feedback)}")
        files = extract_files(work)
        passed, vfb = ctx.verify(files)
        if passed:
            return
        audit = ctx.agent(n - 1, f"Audit this work against the task. Be specific about what to "
                                 f"fix.\n\nTASK:\n{ctx.task}\n\nWORK:\n{work}\n\nTESTS SAID:\n{vfb}")
        feedback = f"{audit}\n\n(verifier: {vfb})"


def tail(feedback):
    return f"\n\n--- SUPERVISOR FEEDBACK ---\n{feedback}" if feedback else ""
