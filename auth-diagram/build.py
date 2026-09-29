"""Merge hand-written section fragments into one .excalidraw file.
"""
import json, sys, glob, os, zlib

here = os.path.dirname(os.path.abspath(__file__))
out = []

def seed(id_, salt):
    return zlib.crc32((id_ + salt).encode()) % 900000 + 100000

for path in sorted(glob.glob(os.path.join(here, "s*.json"))):
    with open(path) as f:
        elems = json.load(f)
    for e in elems:
        t = e["type"]
        e.setdefault("strokeColor", "#1e3a5f")
        e.setdefault("backgroundColor", "transparent")
        e.setdefault("fillStyle", "solid")
        e.setdefault("strokeWidth", 2)
        e.setdefault("strokeStyle", "solid")
        e.setdefault("roughness", 0)
        e.setdefault("opacity", 100)
        e.setdefault("angle", 0)
        e["seed"] = seed(e["id"], "a")
        e["versionNonce"] = seed(e["id"], "b")
        e.setdefault("version", 1)
        e.setdefault("isDeleted", False)
        e.setdefault("groupIds", [])
        e.setdefault("boundElements", None)
        e.setdefault("link", None)
        e.setdefault("locked", False)
        if t in ("rectangle", "diamond"):
            e.setdefault("roundness", {"type": 3} if t == "rectangle" else None)
        if t == "text":
            fs = e.setdefault("fontSize", 16)
            e["fontFamily"] = 3
            e.setdefault("textAlign", "left")
            e["verticalAlign"] = "top"
            e["originalText"] = e["text"]
            e["containerId"] = None
            e["lineHeight"] = 1.25
            e["strokeWidth"] = 1
            lines = e["text"].split("\n")
            h = round(len(lines) * fs * 1.25)
            if "box" in e:
                bx, by, bw, bh = e.pop("box")
                e["x"], e["width"] = bx, bw
                e["y"] = round(by + (bh - h) / 2)
                e["textAlign"] = "center"
            elif "width" not in e:
                e["width"] = round(max(len(l) for l in lines) * fs * 0.6)
            e["height"] = h
        if t in ("arrow", "line"):
            if "from" in e:
                fx, fy = e.pop("from"); tx, ty = e.pop("to")
                e["x"], e["y"] = fx, fy
                e["points"] = [[0, 0], [tx - fx, ty - fy]]
            xs = [p[0] for p in e["points"]]; ys = [p[1] for p in e["points"]]
            e["width"] = max(xs) - min(xs); e["height"] = max(ys) - min(ys)
            if t == "arrow":
                e.setdefault("startBinding", None); e.setdefault("endBinding", None)
                e.setdefault("startArrowhead", None); e.setdefault("endArrowhead", "arrow")
            else:
                e.setdefault("startBinding", None); e.setdefault("endBinding", None)
        out.append(e)

ids = [e["id"] for e in out]
dupes = {i for i in ids if ids.count(i) > 1}
if dupes:
    sys.exit(f"duplicate ids: {dupes}")

doc = {
    "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
    "elements": out,
    "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
    "files": {},
}
dest = os.path.join(here, "auth-architecture.excalidraw")
with open(dest, "w") as f:
    json.dump(doc, f, indent=1)
print(f"wrote {dest} with {len(out)} elements")
