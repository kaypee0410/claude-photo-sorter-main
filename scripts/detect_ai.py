"""Find AI-generated photos and videos from the tags the AI tools leave inside the files.

  python scripts/detect_ai.py                       # check the scanned library (after scan.py)
  python scripts/detect_ai.py --include-edited      # also count real photos changed with AI tools
  python scripts/detect_ai.py --source "/path/to/photos" --copy-to "/path/to/output"
                                                    # quick mode: no scan, just copy what it finds
                                                    # into <output>/AI Photos and Video/

No AI model and no internet needed: it reads the original files only (never changes them) and looks for
  - Content Credentials (C2PA) / IPTC "trainedAlgorithmicMedia", the standard "made by AI" tag that
    ChatGPT/DALL-E, Sora, Adobe Firefly, Google, Meta AI, Microsoft and others write
  - Stable Diffusion / ComfyUI / NovelAI / InvokeAI generation settings saved in PNGs
  - the generator's name in the file's metadata (Midjourney, DALL-E, Leonardo.Ai, Ideogram...)
  - typical download names ("ChatGPT Image ...", "Gemini_Generated_Image_...", "DALL·E 2024-...")

What it cannot see: AI files whose tags were stripped (re-saved, screenshotted, or downloaded from
WhatsApp/Instagram/X, which remove metadata). The Claude labelling step looks at the pictures and adds
the obvious ones of those; see the "ai" and "vai" folders in categories.json.

Writes work/labels/zz_ai_metadata.json (wins over the other labels when the folders are built)
and work/ai_report.csv (every file it flagged and why).
"""
import argparse, csv, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from common import DATA, IMG, LABELS, VID, WORK, categories, load, save

AI_OUT = os.path.join(LABELS, "zz_ai_metadata.json")
REPORT = os.path.join(WORK, "ai_report.csv")
FOLDER = "AI Photos and Video"
EDGE = 1 << 20  # metadata sits at the start or the end of a file: read 1 MB of each

# Made entirely by AI. Long, exact byte strings, so they can't show up by chance inside image data.
MADE = [
    (b"trainedAlgorithmicMedia", "Content Credentials / IPTC tag: made by AI"),
    (b"Made with Google AI", "Google AI tag"),
    (b"Imagined with AI", "Meta AI tag"),
    (b"Midjourney", "Midjourney in metadata"),
    (b"DALL-E", "DALL-E in metadata"),
    (b"DALL\xc2\xb7E", "DALL-E in metadata"),
    (b"OpenAI", "OpenAI in metadata"),
    (b"ChatGPT", "ChatGPT in metadata"),
    (b"Adobe Firefly", "Adobe Firefly in metadata"),
    (b"Stable Diffusion", "Stable Diffusion in metadata"),
    (b"stability.ai", "Stability AI in metadata"),
    (b"Leonardo.Ai", "Leonardo.Ai in metadata"),
    (b"Ideogram", "Ideogram in metadata"),
    (b"NovelAI", "NovelAI in metadata"),
    (b"Bing Image Creator", "Bing Image Creator in metadata"),
    (b"Microsoft Designer", "Microsoft Designer in metadata"),
    (b"sd-metadata", "InvokeAI settings in file"),
]
# A real photo changed with an AI tool (Magic Editor, Generative Fill...). Only counted with --include-edited.
EDITED = [
    (b"compositeWithTrainedAlgorithmicMedia", "Content Credentials / IPTC tag: edited with AI"),
    (b"Edited with Google AI", "Google AI edit tag"),
]
NAMES = re.compile(r"dall[·\-_ ]?e[ _-]|chatgpt[ _-]?image|gemini_generated_image|midjourney|^mj[_-]|^firefly[ _-]"
                   r"|leonardo[_ .-]?ai|^leonardo_|ideogram|stable[_ -]?diffusion|comfyui|^sora[ _-]|grok[-_ ]?image"
                   r"|^grok[_-]|^kling[_-]|^veo[ _-]?\d?[_-]|^pika[_-]|hailuo|dream[_-]?machine|^flux[_-]"
                   r"|ai[_ -]generated|^runway[_-]|bing[_ ]image[_ ]creator", re.I)


def edges(path):
    with open(path, "rb") as f:
        size = os.fstat(f.fileno()).st_size
        if size <= 2 * EDGE:
            return f.read()
        head = f.read(EDGE)
        f.seek(size - EDGE)
        return head + f.read()


def check(path, include_edited=False):
    """Returns (verdict, reason): verdict is "ai", "edited" or None."""
    name = os.path.basename(path)
    try:
        b = edges(path)
    except OSError as e:
        return None, f"unreadable: {e}"
    edited = next((why for tag, why in EDITED if tag in b), None)
    made = next((why for tag, why in MADE if tag in b), None)
    if not made and b"Steps: " in b and b"Sampler: " in b:
        made = "Stable Diffusion settings saved in the PNG"
    if not made and b'"class_type"' in b and (b"KSampler" in b or b"CheckpointLoader" in b):
        made = "ComfyUI workflow saved in the PNG"
    if not made and NAMES.search(name):
        made = "file name from an AI tool"
    if edited and not NAMES.search(name):
        # an AI-edited photo can also carry "made by AI" tags and the tool's name (for the filled-in patch)
        return ("ai" if include_edited else "edited"), edited
    if made:
        return "ai", made
    return None, ""


def ai_keys():
    """The folder key for AI files of each kind: the folder called 'AI Photos and Video', else ai / vai."""
    keys = {}
    for c in categories():
        if c["label"].strip().lower() == FOLDER.lower() or c["key"] in ("ai", "vai"):
            keys.setdefault(c["kind"], c["key"])
    return keys


def copy(src, dst):
    if sys.platform == "darwin" and subprocess.run(["cp", "-c", "-p", src, dst], capture_output=True).returncode == 0:
        return
    shutil.copy2(src, dst)


ap = argparse.ArgumentParser()
ap.add_argument("--include-edited", action="store_true", help="also count real photos edited with AI tools")
ap.add_argument("--source", help="quick mode: check this folder directly, without scanning")
ap.add_argument("--copy-to", help="quick mode: copy what is found into <this folder>/AI Photos and Video/")
args = ap.parse_args()

if args.source:
    src = os.path.expanduser(args.source)
    if not os.path.isdir(src):
        sys.exit(f"Folder not found: {src}")
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(src) for f in fs
                   if os.path.splitext(f)[1].lower() in IMG | VID and not f.startswith("._"))
    recs = [{"id": i, "path": p, "name": os.path.basename(p),
             "kind": "video" if os.path.splitext(p)[1].lower() in VID else "photo"} for i, p in enumerate(files)]
else:
    recs = load(os.path.join(DATA, "inventory.json"))
    if not recs:
        sys.exit("Scan your photos first (scripts/scan.py), or use --source to check a folder directly.")

print(f"Checking {len(recs)} files for AI tags...", flush=True)
found, rows = {}, []
for n, r in enumerate(recs, 1):
    verdict, why = check(r["path"], args.include_edited)
    if verdict:
        rows.append([r["id"], r["name"], r["kind"], "AI-generated" if verdict == "ai" else "edited with AI (not moved)", why, r["path"]])
        if verdict == "ai":
            found[r["id"]] = r
    if n % 50 == 0 or n == len(recs):
        print(f"PROGRESS {n} {len(recs)}", flush=True)

os.makedirs(WORK, exist_ok=True)
with open(REPORT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "file", "kind", "verdict", "reason", "path"])
    w.writerows(rows)

edited = sum(1 for row in rows if row[3].startswith("edited"))
if args.source:
    if args.copy_to and found:
        out = os.path.join(os.path.expanduser(args.copy_to), FOLDER)
        if os.path.abspath(out).startswith(os.path.abspath(src) + os.sep):
            sys.exit("Put the output folder outside the photos folder.")
        os.makedirs(out, exist_ok=True)
        for r in found.values():
            target = os.path.join(out, r["name"])
            if os.path.exists(target):
                b, e = os.path.splitext(r["name"])
                target = os.path.join(out, f"{b}__{r['id']}{e}")
            copy(r["path"], target)
        shutil.copy(REPORT, os.path.join(out, "ai_report.csv"))
        print(f"Copied {len(found)} files into {out} (originals untouched)")
else:
    keys = ai_keys()
    labels = {str(i): keys[r["kind"]] for i, r in found.items() if r["kind"] in keys}
    if len(labels) < len(found):
        print(f"  note: no '{FOLDER}' folder for some kinds in categories.json, {len(found) - len(labels)} files left to the normal folders")
    save(AI_OUT, labels)

print(f"Done: {len(found)} AI-generated ({sum(r['kind'] == 'video' for r in found.values())} videos)"
      + (f", {edited} real photos edited with AI left in their normal folders (use --include-edited to move them too)" if edited else "")
      + f". Details: {REPORT}", flush=True)
