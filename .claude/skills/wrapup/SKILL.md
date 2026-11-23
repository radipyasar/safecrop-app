---
name: wrapup
description: End-of-day wrap-up for the SafeCrop routine. Checks the day's "Done when" list, updates docs/PROGRESS.md (status, log, numbers) and prepares the final commit.
disable-model-invocation: true
---

Wrap up today's SafeCrop work. $ARGUMENTS

1. Find today's day in `docs/ROUTINE.md` (dates shifted by 2 days on 21 Nov, then 1 more day from Day 4: Day 3 = Sat 21 Nov 2026, Day 4 = Mon 23 Nov … Day 11 = Mon 30 Nov; see the table at the top). Go through its "Done when" list and
   check each item for real (run the test, call the endpoint, or look at the file). Mark each one done or not.
2. Update `docs/PROGRESS.md`:
   - set the day's status to `done`, `partly done` or `not started`;
   - add a daily-log entry with three short lines: **Done**, **Left over**, **Blockers**;
   - copy any number measured today into "Numbers for slides" with today's date;
   - add new bugs or ideas to "Bugs and ideas for later";
   - update "Where things are now".
3. If tasks are left over, say which ones move to tomorrow. If the plan is behind, suggest what to cut —
   nice-to-haves first (feedback button, Bangla, home-screen icon, webcam, stats page), never must-haves.
4. Run `git status`. Make sure `.env`, `*.db` and `backend/models/` are not staged. Suggest one commit
   message for the day and ask before committing and pushing.
5. End with a 3-line summary for Nabil in plain words: what works now, what's next tomorrow, anything he must do himself.
