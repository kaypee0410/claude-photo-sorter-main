# Claude photo sorter

Point Claude at your camera roll. It looks at every photo and video, sorts them into folders, finds your duplicates, and you watch it happen on a live dashboard on your own laptop.

![The dashboard sorting a camera roll](docs/preview.gif)

<sub>The demo above uses drawn placeholder images, not real photos.</sub>

- **Sorts photos and videos** into folders like Selfies, Food, Travel, Screenshots, Talking heads and Screen recordings. Use the standard folders or make your own.
- **Finds duplicates**: identical copies, burst shots and re-saved screenshots go to a `_Review` folder, with a list of which copy was kept.
- **Never touches your originals.** It only reads them and makes sorted copies. On a Mac the copies take no extra space.
- **Runs on your computer.** Your photos are not uploaded anywhere.
- **Finds AI-generated photos and videos** and puts them in an **AI Photos and Video** folder.

<sub>Based on [kairothq/claude-photo-sorter](https://github.com/kairothq/claude-photo-sorter) (MIT). This copy adds Windows support and the AI Photos and Video folder.</sub>

## Start here (no coding needed)

You need a Mac and a Claude plan. Windows and Linux work too, with a few less conveniences.

**1. Install Claude Code** from [claude.com/claude-code](https://claude.com/claude-code). Then open the **Terminal** app (press `⌘ Space`, type *Terminal*, press Enter), type `claude` and press Enter.

**2. Paste this to Claude:**

```
Set up and open https://github.com/kairothq/claude-photo-sorter
```

Claude downloads it, sets it up and opens the dashboard in your browser.

**3. In the dashboard:**

1. **Choose folder**: pick the folder with your photos (a Google Photos or Apple Photos export, or any folder).
2. Pick where the sorted copies should go. The default is right next to your photos.
3. Press **Start sorting**.

It shows how long it usually takes, then sorts on its own while you watch every photo fly into its folder. About 4 minutes for 1,000 photos.

<details>
<summary>Don't have your photos on your computer yet?</summary>

- **Google Photos:** go to [takeout.google.com](https://takeout.google.com), select only Google Photos, download, and unzip everything into one folder.
- **iPhone or Apple Photos:** in Photos on your Mac, select all, then File > Export > Export Unmodified Originals, into a new folder.
</details>

<details>
<summary>On Windows</summary>

1. In PowerShell: `irm https://claude.ai/install.ps1 | iex`, then `winget install Git.Git Python.Python.3.12 Gyan.FFmpeg`. Close and reopen the terminal.
2. Open this folder in VS Code, open the terminal (Terminal > New Terminal), and run `claude`. Ask it to "set up and open the photo sorter".
3. Or by hand: `.\setup.bat` once, then `.\start.bat`. Later, double-click **Open Photo Sorter.bat**.

On Windows the sorted copies are real copies, so they take as much space as the originals.
</details>

## Using it again

The dashboard lives at **http://127.0.0.1:8765** while it's running. To open it again later, either:

- double-click **Open Photo Sorter.command** in the `claude-photo-sorter` folder (it's in your home folder), or
- tell Claude "open my photo sorter".

Press **New sort** to sort a different folder, or send the copies somewhere else.

## The dashboard

| | |
|---|---|
| **Sort with Claude** | Before sorting: asks for anything missing, then starts. After sorting: replays the animation (good for screen recording). Add `?d=20` to the address for a slower take. |
| **New sort** | Pick a new photos folder and a new place for the copies. |
| **Advanced** (in the setup card) | See the folders that will be made, remove any, or press **+** to add your own. Choose Claude or Jev. Try 200 photos first. |
| **Click a folder** | Browse everything in it. Click a photo to see it full size, flip with the arrow keys, and **Move to** another folder if it's wrong. |
| **Edit folders** | Rename folders and describe what goes in each. |
| **Open sorted folder** | Opens the result in Finder. |
| ☀ / ☾ | Light or dark. |

Want a look without your own photos? Run `./start.sh --demo`.

## How it works

1. **Scan**: makes a small preview of every file and a fingerprint to spot copies. Your originals are only read.
2. **Duplicates**: compares fingerprints, plus a pixel check for screenshots so similar app screens aren't mistaken for copies.
3. **AI check**: looks inside each original for the tags AI tools leave (Content Credentials, IPTC "made by AI", Stable Diffusion/ComfyUI settings, Midjourney/DALL-E/Firefly names, "ChatGPT Image…" file names). Those files go to **AI Photos and Video**. No extra model or internet needed. Details in `work/ai_report.csv`.
4. **Labels**: runs Claude Code in the background (`claude -p`), four at a time, each looking at about 90 previews and picking a folder for each. This uses your Claude plan and needs no API key. Claude also sends files that are *obviously* AI-made (AI art, warped hands, garbled text) to **AI Photos and Video**, which catches AI pictures whose tags were stripped by WhatsApp, Instagram or a screenshot. Realistic AI photos without tags can't be spotted reliably by any tool, so some will stay in the normal folders.
5. **Folders**: copies each file into its folder, and duplicates into `_Review/duplicates`. Writes `sorted.csv` and `duplicates.csv`.

### Claude or Jev?

| | Claude (default) | Jev (Advanced, optional) |
|---|---|---|
| What | Claude Code reads contact sheets of 30 previews | [TypeSafe's](https://typesafe.ai) Jev 1.14 image model, one question per file |
| Cost | Included in your Claude plan | Billed per file, about 980 tokens each. Shows an estimate and asks first |
| Speed | About a minute per 1,000 files | About 75 seconds per 1,000 files |
| Setup | Nothing | Put `JEV_KEY=your-key` in a `.env` file in this folder |

## Privacy

- The dashboard only listens on `127.0.0.1`, so nothing else on your network can reach it.
- Previews, labels and the file list stay in `dashboard/data/` and `work/`, which are never committed.
- With Claude, the small previews are read by Claude Code the same way as anything else you share with it. With Jev, a 280px preview of each file goes to TypeSafe's API. Originals never leave your computer.

## Running it by hand

```bash
./setup.sh          # once: Python packages into .venv/
./start.sh          # opens http://127.0.0.1:8765
```

Every step is also a script in `scripts/` (`scan.py`, `dupes.py`, `detect_ai.py`, `label_claude.py`, `label_jev.py`, `apply.py`). To pull only the AI files out of a folder without a full sort: `.venv/bin/python scripts/detect_ai.py --source "<photos>" --copy-to "<output>"`. Agents read `CLAUDE.md` (or `AGENTS.md`) for the full playbook. Needs Python 3.9+, and ffmpeg for video previews (`brew install ffmpeg`).

## License

MIT
