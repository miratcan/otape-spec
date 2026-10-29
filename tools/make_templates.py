#!/usr/bin/env python3
"""Generate the oTAPE 1.0 artwork templates (SVG, 1:1 millimetres).

    python3 tools/make_templates.py            # writes templates/*.svg

Every number comes from geometry/otape-geometry-1.0.json, the machine-readable
twin of the geometry tables in the specification. Standard library only.

Part of the oTAPE specification · © 2026 Jan Osio · CC BY 4.0
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G = json.loads((ROOT / "geometry" / "otape-geometry-1.0.json").read_text(encoding="utf-8"))
OUT = ROOT / "templates"
PPM = G["resolution"]["recommended_px_per_mm"]
MIN_PPM = G["resolution"]["minimum_px_per_mm"]


def f(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s != "-0" else "0"


def px(mm: float, per_mm: float = PPM) -> int:
    return int(mm * per_mm + 0.5)


class SVG:
    def __init__(self, width: float, height: float, margin: float = 14.0):
        self.width, self.height, self.margin = width, height, margin
        self.body: list[str] = []

    def add(self, s: str) -> None:
        self.body.append(s)

    def rect(self, x: float, y: float, w: float, h: float, cls: str, rx: float = 0) -> None:
        self.add(f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}"/>')

    def circle(self, cx: float, cy: float, d: float, cls: str) -> None:
        self.add(f'<circle class="{cls}" cx="{f(cx)}" cy="{f(cy)}" r="{f(d / 2)}"/>')

    def text(self, s: str, x: float, y: float, cls: str = "note", anchor: str = "start", rotate: float = 0) -> None:
        t = f' transform="rotate({f(rotate)} {f(x)} {f(y)})"' if rotate else ""
        self.add(f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{t}>{s}</text>')

    def hdim(self, x0: float, x1: float, y: float, label: str) -> None:
        self.add(f'<path class="dim" d="M{f(x0)} {f(y - 1)}V{f(y + 1)}M{f(x0)} {f(y)}H{f(x1)}M{f(x1)} {f(y - 1)}V{f(y + 1)}"/>')
        self.text(label, (x0 + x1) / 2, y - 0.6, "small", "middle")

    def vdim(self, y0: float, y1: float, x: float, label: str) -> None:
        self.add(f'<path class="dim" d="M{f(x - 1)} {f(y0)}H{f(x + 1)}M{f(x)} {f(y0)}V{f(y1)}M{f(x - 1)} {f(y1)}H{f(x + 1)}"/>')
        self.text(label, x + 1.2, (y0 + y1) / 2, "small", "middle", 90)

    def write(self, name: str, title: str) -> None:
        m = self.margin
        w = max(self.width + 2 * m, 190)
        h = self.height + 2 * m + 4
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{f(w * 4)}" height="{f(h * 4)}" viewBox="{f(-m)} {f(-m)} {f(w)} {f(h)}">
<title>{title}</title>
<style>
  text {{ font-family: Helvetica, Arial, sans-serif; fill: #333; }}
  .trim {{ fill: #fff; stroke: #111; stroke-width: 0.25; }}
  .safe {{ fill: none; stroke: #2a9d8f; stroke-width: 0.2; stroke-dasharray: 1 0.6; }}
  .keep {{ fill: rgba(230,57,70,0.18); stroke: #e63946; stroke-width: 0.2; }}
  .zone {{ fill: rgba(69,123,157,0.12); stroke: #457b9d; stroke-width: 0.15; }}
  .fold {{ stroke: #999; stroke-width: 0.2; stroke-dasharray: 2 1; }}
  .dim {{ stroke: #666; stroke-width: 0.12; fill: none; }}
  .note {{ font-size: 1.8px; }}
  .small {{ font-size: 1.3px; fill: #555; }}
  .head {{ font-size: 2.6px; font-weight: bold; }}
</style>
{chr(10).join(self.body)}
</svg>
"""
        (OUT / name).write_text(svg, encoding="utf-8")
        print("wrote", OUT.name + "/" + name)


def cassette_face() -> None:
    shell, mech, label = G["shell"], G["mechanism"], G["label"]
    win = mech["window"]
    svg = SVG(shell["width"], shell["height"])
    svg.rect(0, 0, shell["width"], shell["height"], "trim", shell["corner_radius"])
    lx, ly = label["origin_on_shell"]
    svg.rect(lx, ly, label["width"], label["height"], "zone", label["corner_radius"])
    svg.add('<polygon class="zone" points="' + " ".join(f"{f(x)},{f(y)}" for x, y in shell["head_opening"]) + '"/>')
    svg.rect(win["x"], win["y"], win["width"], win["height"], "keep", win["corner_radius"])
    for hub in (mech["left_hub"], mech["right_hub"]):
        svg.circle(*hub, mech["hub_hole_diameter"], "keep")
    for s in shell["screws"]:
        svg.circle(*s, shell["screw_diameter"], "dim")
    for hole in shell["head_holes"]:
        svg.circle(*hole["center"], hole["diameter"], "dim")
    hs = shell["head_slot"]
    svg.rect(hs["x"], hs["y"], hs["width"], hs["height"], "dim")
    w, h = shell["width"], shell["height"]
    svg.text(f"oTAPE 1.0 · cassette_face_a / cassette_face_b · {f(w)} × {f(h)} mm · "
             f"{px(w)} × {px(h)} px @ {PPM} px/mm (min {px(w, MIN_PPM)} × {px(h, MIN_PPM)})", 0, -8, "head")
    svg.text(f"Red = must be transparent (window, hub holes Ø {f(mech['hub_hole_diameter'])} mm). "
             f"Blue = label area and head opening. Corner radius {f(shell['corner_radius'])} mm.", 0, -4.5)
    svg.text(f"label {f(label['width'])} × {f(label['height'])} at ({f(lx)}, {f(ly)})", lx + 1, ly + label["height"] - 1, "small")
    for hub in (mech["left_hub"], mech["right_hub"]):
        svg.text(f"hub {f(hub[0])}, {f(hub[1])}", hub[0], hub[1] + 11, "small", "middle")
    svg.text(f"window {f(win['width'])} × {f(win['height'])}", win["x"] + win["width"] / 2, win["y"] - 0.8, "small", "middle")
    svg.hdim(0, w, h + 5, f"{f(w)} mm")
    svg.vdim(0, h, w + 5, f"{f(h)} mm")
    lh, rh = mech["left_hub"], mech["right_hub"]
    svg.hdim(lh[0], rh[0], lh[1] - 10.5, f"hub centres {f(rh[0] - lh[0])} mm")
    svg.write("cassette-face.svg", "oTAPE cassette face template")


def label_template() -> None:
    L, mech = G["label"], G["mechanism"]
    ox, oy = L["origin_on_shell"]
    win = mech["window"]
    m = L["keep_out_margin"]
    svg = SVG(L["width"], L["height"])
    svg.rect(0, 0, L["width"], L["height"], "trim", L["corner_radius"])
    si = L["safe_inset"]
    svg.rect(si, si, L["width"] - 2 * si, L["height"] - 2 * si, "safe", L["corner_radius"])
    svg.rect(win["x"] - ox - m, win["y"] - oy - m, win["width"] + 2 * m, win["height"] + 2 * m, "keep", win["corner_radius"])
    for hub in (mech["left_hub"], mech["right_hub"]):
        svg.circle(hub[0] - ox, hub[1] - oy, mech["hub_hole_diameter"] + 2 * m, "keep")
    z = L["zones"]
    for key in ("side_letter_box", "title_line", "side_title_line", "bottom_band", "type_badge"):
        b = z[key]
        svg.rect(b["x"], b["y"], b["width"], b["height"], "zone")
    b = z["side_letter_box"]
    svg.text("A", b["x"] + b["width"] / 2, b["y"] + b["height"] - 1.5, "head", "middle")
    b = z["title_line"]
    svg.text(f"title (cassette.title) · baseline {f(b['baseline'])} mm", b["x"] + 1, b["baseline"] - 0.2)
    b = z["side_title_line"]
    svg.text(f"side title (sides.A.title) · baseline {f(b['baseline'])} mm", b["x"] + 1, b["baseline"])
    b = z["bottom_band"]
    svg.text("bottom band (stripes / gradient)", 2.5, b["y"] + 3)
    b = z["type_badge"]
    svg.text("type C60", b["x"] + b["width"] - 0.5, b["y"] + b["height"] - 1.2, anchor="end")
    svg.text(f"keep-out: window + hub holes + {f(m)} mm", win["x"] - ox + win["width"] / 2, win["y"] - oy + win["height"] / 2 + 0.6,
             "small", "middle")
    w, h = L["width"], L["height"]
    svg.text(f"oTAPE 1.0 · label_a / label_b · {f(w)} × {f(h)} mm · {px(w)} × {px(h)} px @ {PPM} px/mm "
             f"(min {px(w, MIN_PPM)} × {px(h, MIN_PPM)})", 0, -8, "head")
    svg.text(f"Green dashed = safe area ({f(si)} mm). Red = keep-out, must be transparent. "
             f"Blue = lettering zones of the procedural label. Corner radius {f(L['corner_radius'])} mm.", 0, -4.5)
    svg.hdim(0, w, h + 5, f"{f(w)} mm")
    svg.vdim(0, h, w + 5, f"{f(h)} mm")
    svg.write("label.svg", "oTAPE label template")


def jcard_template() -> None:
    J = G["jcard"]
    H, fw, sw, front_w = J["height"], J["flap_width"], J["spine_width"], J["front_width"]
    total = fw + sw + front_w
    svg = SVG(total, H)
    panels = {"flap": (0, fw), "spine": (fw, sw), "front": (fw + sw, front_w)}
    for x, w in panels.values():
        svg.rect(x, 0, w, H, "trim")
    for name, (x, w) in panels.items():
        inset = J["safe_inset"] if name == "front" else J["spine_safe_inset"]
        svg.rect(x + inset, inset, w - 2 * inset, H - 2 * inset, "safe")
    for x in (fw, fw + sw):
        svg.add(f'<line class="fold" x1="{f(x)}" y1="-4" x2="{f(x)}" y2="{f(H + 4)}"/>')
    for name, (x, w) in (("jcard_flap", panels["flap"]), ("jcard_spine", panels["spine"])):
        svg.text(name, x + w / 2, 8, anchor="middle")
        svg.text(f"{px(w)} × {px(H)} px", x + w / 2, 11, "small", "middle")
    sx = fw + sw / 2
    svg.text("SPINE TEXT READS TOP → BOTTOM", sx - 0.6, 20, rotate=90)
    svg.add(f'<path class="dim" d="M{f(sx + 2.5)} 20V{f(H - 20)}l-0.8 -1.6m0.8 1.6l0.8 -1.6"/>')
    fx = fw + sw + front_w / 2
    svg.text("jcard_front (cover)", fx, 8, "head", "middle")
    svg.text(f"{px(front_w)} × {px(H)} px @ {PPM} px/mm", fx, 12, anchor="middle")
    svg.text(f"safe area {f(J['safe_inset'])} mm", fx, H - 5, "small", "middle")
    svg.text(f"oTAPE 1.0 · J-card outside, unfolded: flap | spine | front · {f(total)} × {f(H)} mm. "
             "Trim size, no bleed. Dashed grey = folds.", 0, -8, "head")
    svg.text(f"Each panel is its own image in the file. Booklet panels ({f(J['booklet_panel_width'])} × {f(H)} mm) "
             "continue to the right of the front when unfolded.", 0, -4.5)
    svg.hdim(0, fw, H + 5, f(fw))
    svg.hdim(fw, fw + sw, H + 5, f(sw))
    svg.hdim(fw + sw, total, H + 5, f"{f(front_w)} mm")
    svg.vdim(0, H, total + 5, f"{f(H)} mm")
    svg.write("jcard-outside.svg", "oTAPE J-card template")


def booklet_template() -> None:
    J = G["jcard"]
    w, h = J["booklet_panel_width"], J["height"]
    svg = SVG(w, h)
    svg.rect(0, 0, w, h, "trim")
    si = J["safe_inset"]
    svg.rect(si, si, w - 2 * si, h - 2 * si, "safe")
    svg.text("booklet panel NN", w / 2, 40, "head", "middle")
    svg.text(f"{px(w)} × {px(h)} px @ {PPM} px/mm", w / 2, 45, anchor="middle")
    svg.text(f"safe area {f(si)} mm", w / 2, h - 5, "small", "middle")
    svg.text(f"oTAPE 1.0 · booklet.panels[] · {f(w)} × {f(h)} mm, portrait, reading order", 0, -8, "head")
    svg.hdim(0, w, h + 5, f"{f(w)} mm")
    svg.vdim(0, h, w + 5, f"{f(h)} mm")
    svg.write("booklet-panel.svg", "oTAPE booklet panel template")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cassette_face()
    label_template()
    jcard_template()
    booklet_template()
