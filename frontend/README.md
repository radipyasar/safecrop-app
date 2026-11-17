# SafeCrop web app: home page (UI preview)

The home page of the SafeCrop web app, built with React (Vite). It fills the whole browser window:

- **Left menu**: Home, Check a leaf, Diseases, History, Profile
- **Check a sick leaf**: the main card, with "Upload a photo", "Use camera", a drop area for a leaf photo,
  and what happens next (Photo check, Compare, Get advice)
- **Diseases SafeCrop knows**: the 8 diseases (one row of picture cards on wide screens)
- A note that SafeCrop gives a best guess, not a final diagnosis

It adjusts to the screen: on a laptop or desktop you get the left menu and the full-width cards; on a phone or a
narrow window you get one column with a bar at the bottom.

This is a **UI preview with sample data**. The buttons don't do anything yet: no photo is uploaded and no model
(CLIP or Gemini) runs.

## Run it in VS Code

You need **Node.js 18 or newer** (the LTS version from https://nodejs.org). Check in a terminal: `node -v`.

1. Unzip `safecrop-web.zip`. In VS Code: **File > Open Folder** > choose the `safecrop-web` folder
   (the one that contains `package.json`).
2. Open a terminal: **Terminal > New Terminal**.
3. First time only, install the packages (about 1 minute; makes a `node_modules` folder):
   ```
   npm install
   ```
4. Start the app:
   ```
   npm run dev
   ```
   Your browser opens **http://localhost:5173** by itself. If it doesn't, Ctrl+click (Cmd+click on a Mac)
   the `Local:` link in the terminal.
5. Leave the terminal running while you use it. Saved code changes show up in the browser straight away.
6. To stop: click in the terminal and press **Ctrl+C**.

Next time, just open the folder and run `npm run dev`.

Tip: to see the phone layout, make the browser window narrow, or press F12 and click the phone/tablet icon.

## If something goes wrong

| Problem | Fix |
| --- | --- |
| `npm` is not recognized / command not found | Install Node.js LTS, then close and reopen VS Code |
| Windows: "running scripts is disabled on this system" | In the terminal's **+ ⌄** menu pick **Command Prompt** and run the commands there, or run once in PowerShell: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| "Port 5173 is in use" or a different port appears | Another app (for example the earlier SafeCrop preview) is still running: stop it with Ctrl+C, or open the `Local:` link Vite prints |
| A blank page when you double-click `index.html` | That doesn't work for React apps: use `npm run dev` |
| Errors during `npm install` | Delete the `node_modules` folder and run `npm install` again |

## Files

```
index.html                     the page the app is mounted into
src/main.jsx                   starts React, loads the fonts and styles
src/App.jsx                    the layout: left menu, top bar and bottom bar on phones
src/HomePage.jsx               the home page and its cards
src/components/Sidebar.jsx     the left menu
src/components/ScanCard.jsx    "Check a sick leaf" (upload / camera / drop area)
src/components/BottomNav.jsx   the bottom bar (phones)
src/components/Leaf.jsx        the drawn leaves used instead of real photos
src/components/Icons.jsx       line icons
src/data/sample.js             sample data (later: from the back end)
src/styles.css                 all styles, including the screen-size rules at the end
```

Other commands: `npm run build` makes a production build in `dist/`; `npm run preview` serves that build.
