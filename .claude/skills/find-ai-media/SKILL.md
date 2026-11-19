---
name: find-ai-media
description: Find AI-generated photos and videos in the user's library and copy them into an "AI Photos and Video" folder. Use when they ask to find, separate, pull out or check for AI pictures, AI images, AI videos, ChatGPT/Gemini/Midjourney images or fake photos.
---

# Find AI photos and videos

Never move, rename or delete originals. Everything here makes copies. Keep messages short and plain.

## Pick the route (ask with numbers if it isn't clear)

1. **Quick: only pull out the AI files.** No scan, no labels, takes seconds:
   ```bash
   .venv/bin/python scripts/detect_ai.py --source "<photos folder>" --copy-to "<output folder>"
   ```
   Copies go to `<output folder>/AI Photos and Video/`, with `ai_report.csv` next to them saying why each file was picked.
2. **Full sort.** The dashboard's **Start sorting** already runs the AI check before labelling, so AI files land in **AI Photos and Video** alongside the other folders. Nothing extra to do.
3. **Already sorted earlier, before this folder existed.** Make sure `categories.json` has the `ai` and `vai` folders, then re-run labels and folders so both the tag check and Claude's look are applied:
   ```bash
   .venv/bin/python scripts/detect_ai.py
   .venv/bin/python scripts/label_claude.py
   .venv/bin/python scripts/apply.py "<output folder>"
   ```
   Adding folders changes the categories, so the dashboard relabels on its next **Start sorting** anyway.

Output folder must be outside the photos folder.

## Real photos edited with AI

Pixel Magic Editor, Samsung AI edits and Photoshop Generative Fill tag the photo as "edited with AI". These stay in their normal folders by default and are listed in the report as "edited with AI". If the user wants them in the AI folder too, add `--include-edited`.

## A second look by Claude (optional, for the quick route)

The tag check misses AI files whose tags were stripped (WhatsApp, Instagram, X, screenshots). To catch the obvious ones:

1. `.venv/bin/python scripts/scan.py "<photos folder>"` then `.venv/bin/python scripts/sheets.py`.
2. Read each `work/sheets/sheet_*.jpg`. List only ids that are clearly AI-made: AI art styles, garbled text, warped hands or faces, impossible scenes. When unsure, leave it out.
3. Show the user the list (file names from `dashboard/data/inventory.json`) and copy those files into the same `AI Photos and Video` folder only after they say yes.

## What to tell the user

- Tagged files (ChatGPT/DALL-E, Sora, Gemini/Google, Meta AI, Firefly, Midjourney, Stable Diffusion, ComfyUI downloads) are found reliably.
- Realistic AI photos with no tags can't be detected reliably by Claude or by any detector, so a few may stay in the normal folders, and Claude's visual guess can be wrong. They can fix any file from the dashboard with **Move to**.
- No extra AI model or API key is needed.
