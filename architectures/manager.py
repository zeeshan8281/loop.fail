"""manager — agent[0] plans and delegates subtasks to the workers, then synthesizes.

The manager assigns one subtask per worker, collects their replies, and writes the
final files. Re-runs with verifier feedback until solved or the kill switch trips.
"""
from loop_io import extract_files


def run(ctx):
    n = len(ctx.agents)
    feedback = ""
    while ctx.should_continue():
        assignment = ctx.agent(0, f"{ctx.context_blob()}\n\nYou are the manager. Break this into "
                                  f"{n - 1} concrete subtasks, one per worker, numbered.{fb(feedback)}")
        results = []
        for i in range(1, n):  # workers
            results.append(ctx.agent(i, f"{ctx.context_blob()}\n\n--- MANAGER ASSIGNMENT ---\n"
                                        f"{assignment}\n\nYou are worker {i}. Do your subtask."))
        joined = "\n\n".join(f"--- WORKER {i+1} ---\n{r}" for i, r in enumerate(results))
        final = ctx.agent(0, f"{ctx.context_blob()}\n\nSynthesize the workers' results into the "
                             f"final output files.\n{joined}")
        passed, vfb = ctx.verify(extract_files(final))
        if passed:
            return
        feedback = vfb


def fb(feedback):
    return f"\n\n--- VERIFIER FEEDBACK ---\n{feedback}" if feedback else ""
