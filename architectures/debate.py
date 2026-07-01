"""debate — every agent answers, sees everyone else's answers, then revises.

agent[-1] is the moderator: it reads the revised answers and picks the final output.
Good for hard reasoning (task 003). Re-runs with verifier feedback if rejected.
"""
from loop_io import extract_files


def run(ctx):
    n = len(ctx.agents)
    feedback = ""
    while ctx.should_continue():
        base = ctx.context_blob() + (f"\n\n--- VERIFIER FEEDBACK ---\n{feedback}" if feedback else "")
        first = [ctx.agent(i, base) for i in range(n - 1)]
        board = "\n\n".join(f"--- AGENT {i+1} ---\n{a}" for i, a in enumerate(first))
        revised = [ctx.agent(i, f"{base}\n\nOther agents proposed:\n{board}\n\nRevise your answer.")
                   for i in range(n - 1)]
        revboard = "\n\n".join(f"--- AGENT {i+1} ---\n{a}" for i, a in enumerate(revised))
        final = ctx.agent(n - 1, f"{base}\n\nYou are the moderator. Pick/merge the best answer and "
                                 f"emit the final output files.\n{revboard}")
        passed, feedback = ctx.verify(extract_files(final))
        if passed:
            return
