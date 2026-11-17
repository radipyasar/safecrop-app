---
name: today
description: Start a day of the SafeCrop web-app routine. Reads that day's tasks from docs/ROUTINE.md and what is already done from docs/PROGRESS.md, then works through the blocks one task at a time.
argument-hint: [day-number, e.g. 3]
disable-model-invocation: true
---

Start SafeCrop routine day $ARGUMENTS.

1. Read `docs/PROGRESS.md`. If no day number was given, work it out from today's date
   (Day 1 = Tue 17 Nov 2026, Day 11 = Fri 27 Nov 2026). If an earlier day is unfinished, say which
   tasks are left and ask whether to finish those first.
2. Read that day's section in `docs/ROUTINE.md` (the heading starts with `## Day N —`), including its
   "Done when" and "If you get stuck" parts.
3. Look at the current code so the plan fits what is really there.
4. Give Nabil a short plan in plain words:
   - the three blocks and their tasks (one line each),
   - anything only he can do (accounts, keys, Colab GPU runs, phone photos) — as a numbered list,
   - which tasks are already done.
   Then wait for "go" before changing files.
5. Work one task at a time. Before each task say in one sentence what you will do. After it, run the
   matching check (test, command, or page to open) and tell Nabil how to see the result himself.
6. When a task is done, tick its box in `docs/ROUTINE.md` (`- [ ]` → `- [x]`).
7. At the end of each block: run `git status`, make sure `.env` and `backend/models/` are not staged,
   suggest a commit message like `Day 3: /api/check returns disease`, and ask before committing.
8. Follow every rule in `CLAUDE.md` (no card, no keys in code, CLIP decides the label, no chemical doses,
   no stored photos, plain words).
