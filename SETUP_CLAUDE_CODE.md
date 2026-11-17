# Set up Claude Code in VS Code for the SafeCrop web app

These files tell Claude Code the whole SafeCrop story and the 17–27 Nov routine, every time you open a
new chat. You set this up once (about 10 minutes).

## What is in this kit

| File | What it does |
| --- | --- |
| `CLAUDE.md` | Claude Code reads this **automatically at the start of every chat**: what SafeCrop is, your rules (no card, no keys in code, plain words…), the tech stack, folders, API and commands. It also pulls in the two files below. |
| `docs/PROJECT_STORY.md` | The project story and every result the app relies on (E0–E4, recipe B, noisy album, why E4). Loaded automatically. |
| `docs/PROGRESS.md` | What's done, what's next, numbers for slides. Loaded automatically, so Claude always knows where you are. |
| `docs/ROUTINE.md` | The 11-day routine as a tick-box list. Claude reads the day it needs (not loaded every time, to save space). |
| `docs/SafeCrop_webapp_routine_17-27Nov2026.pdf` | The same routine as the PDF, for you. |
| `docs/results/` | Full result tables, read only when a task needs them. |
| `.claude/skills/today/` | Adds the command **`/today 1`** (or `/today 2` …): starts that day's tasks. |
| `.claude/skills/wrapup/` | Adds the command **`/wrapup`**: end-of-day check, updates PROGRESS.md, prepares the commit. |
| `.gitignore` | Keeps `.env`, model files and `node_modules` out of GitHub. |

## Step 1 — Make the project folder

1. Make a new folder called `safecrop-app`.
2. Move your current front-end folder (the one with `package.json`, called `FrontEnd` / `safecrop-web`) into it
   and rename it `frontend`.
3. Unzip this kit **into `safecrop-app`**, so `CLAUDE.md` sits next to `frontend/`:

```
safecrop-app/
  CLAUDE.md
  .gitignore
  .claude/skills/today/SKILL.md
  .claude/skills/wrapup/SKILL.md
  docs/ ...
  frontend/        (your React app)
```

(On Windows, `.claude` and `.gitignore` start with a dot; that's normal. If you don't see them, turn on
View → Show → Hidden items in File Explorer.)

## Step 2 — Install Claude Code in VS Code (skip if already installed)

1. Open VS Code (version 1.94 or newer). Press `Ctrl+Shift+X`, search **Claude Code** (by Anthropic), click **Install**.
2. Click the **Spark** icon (in the left bar, or top-right of an open file) to open the Claude Code panel.
3. Click **Sign in** and finish in the browser with your Claude account (any paid Claude plan works; no API key needed).

## Step 3 — Open the right folder

1. In VS Code: **File → Open Folder… → `safecrop-app`** (the folder that has `CLAUDE.md`, not `frontend`).
2. Open the Claude Code panel and start a **new** chat (old chats don't reload the files).

## Step 4 — Check that Claude knows everything

1. Type `/memory`. You should see `CLAUDE.md` in the list of loaded files.
2. Ask: **"In 5 lines: what is SafeCrop, which model does the app use and why, and what is today's task?"**
   It should say E4 (fine-tuned CLIP + noisy copies, most robust on recipe B) and name today's day.
3. Type `/` and check that **today** and **wrapup** appear in the menu.

## Step 5 — Use it every day

- Start of the day: **`/today 1`** (then `/today 2` tomorrow, and so on). Claude reads the day, shows you a short
  plan and what only you can do, and waits for "go".
- During the day: ask for one task at a time, e.g. *"Do Block B task 3"*. Claude ticks the box in `docs/ROUTINE.md`
  when it's done.
- End of the day: **`/wrapup`**. Claude checks the "Done when" list, updates `docs/PROGRESS.md` and suggests a commit.
- Start a fresh chat each day; `CLAUDE.md` and `PROGRESS.md` carry everything over.

## Step 6 (for Day 2) — Let Claude see the research repo

Day 2 needs code from `NabilRafi/SafeCrop` (`finetune.py`, `noise.py`, the photo-check code).

1. Clone it next to the app: `safecrop-app` and `SafeCrop` in the same parent folder.
2. In the Claude Code chat type: `/add-dir ../SafeCrop`

That repo has its own `CLAUDE.md` for the fine-tuning work; that's fine, the two work together.

## Keep it up to date

- If something big changes (a new decision, a new result), ask Claude: *"Add this to PROJECT_STORY.md"*.
- Keep `CLAUDE.md` short (under ~200 lines). Long details go in `docs/`.
- Commit `CLAUDE.md`, `docs/` and `.claude/skills/` to GitHub so your teammate's Claude Code knows the same things.
- Never write your Gemini key or Hugging Face token in any of these files.
