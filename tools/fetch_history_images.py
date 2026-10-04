"""
Downloads public-domain / CC-licensed history images for the classroom tab.

Run once with internet access:  python tools/fetch_history_images.py
Saves into assets/images/history/. The app never downloads at runtime —
missing files render an offline placeholder instead.
All files below are from Wikimedia Commons (public domain unless noted).
"""

import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.path.dirname(HERE), "assets", "images", "history")

# (filename, commons URL, max width px)
# URLs are the canonical upload.wikimedia.org paths resolved via the
# Commons API (query → imageinfo → url). License/attribution → CREDITS.md.
IMAGES = [
    (
        "young_portrait.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/9/9f/Thomas_Young_%28scientist%29.jpg",
        500,
    ),
    (
        "fringes.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/9/95/2slits_quantum.jpg",
        800,
    ),
    (
        "hitachi_buildup.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/c/c7/Double-slit_experiment_results_Tonomura_2.jpg",
        800,
    ),
    (
        "c60.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/0/0f/Buckminsterfullerene-perspective-3D-balls.png",
        800,
    ),
]


def main() -> int:
    os.makedirs(DEST, exist_ok=True)
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        has_pil = False
        print("Pillow not found — saving originals without resize.")

    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "YoungDoubleSlitEduApp/1.0 (classroom use; contact: local)")]
    urllib.request.install_opener(opener)

    ok = 0
    for fname, url, max_w in IMAGES:
        path = os.path.join(DEST, fname)
        try:
            print(f"Downloading {fname} ...")
            urllib.request.urlretrieve(url, path)
            if has_pil:
                with Image.open(path) as im:
                    if im.width > max_w:
                        ratio = max_w / im.width
                        im = im.resize((max_w, int(im.height * ratio)), Image.LANCZOS)
                        if im.mode in ("RGBA", "P"):
                            im = im.convert("RGB")
                        im.save(path, "JPEG", quality=85)
            print(f"  saved {path} ({os.path.getsize(path) // 1024} KB)")
            ok += 1
        except Exception as e:
            print(f"  FAILED {fname}: {e}")
    print(f"Done: {ok}/{len(IMAGES)} images.")
    return 0 if ok == len(IMAGES) else 1


if __name__ == "__main__":
    sys.exit(main())
