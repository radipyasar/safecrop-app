---
name: wrapup
description: End-of-day wrap-up for the SafeCrop routine. Checks the day's "Done when" list, updates docs/PROGRESS.md (status, log, numbers) and prepares the final commit.
disable-model-invocation: true
---

Wrap up today's SafeCrop work. $ARGUMENTS

1. Find today's day in `docs/ROUTINE.md` (Day 1 = Tue 17 Nov, Day 2 = Wed 18–Thu 19, Day 3 = Sat 21 Nov, Day 4 = Mon 23 Nov, Day 5 + Day 6 Block B + Day 7 = Tue 24 Nov, Day 8 + Day 6 Block A = Wed 25 Nov, Days 9–11 = Thu 26 Nov (plan shortened on 24 Nov), Week 11 update = Mon 30 Nov; one date can hold several days — check each one; see the table at the top). Go through its "Done when" list and
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
