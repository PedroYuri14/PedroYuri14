"""Render real GitHub contributions as an isometric city using svgwrite.

The SVG, PNG and GIF share the same geometry. No random contributions or dates.
"""
import argparse
from datetime import date, timedelta
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw, ImageFont
import svgwrite

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "scripts/commit-city-config.json").read_text())
WIDTH, HEIGHT = 1600, 1080
BG, SURFACE, TEXT = "#0D1117", "#161B22", "#E6EDF3"
MUTED, BLUE, GREEN, PURPLE = "#A7B3C2", "#58A6FF", "#3FB950", "#BC8CFF"
FONT = ROOT / "assets/fonts/JetBrainsMono-Regular.ttf"
QUERY = """query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def write_changed(path, content):
    """Avoid overwriting identical output or embedding changing timestamps."""
    path = Path(path)
    if isinstance(content, str):
        content = content.encode("utf-8")
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)
    return True


def normalize_calendar(calendar, username, start, end):
    days = []
    seen = set()
    for week in calendar["weeks"]:
        for raw in week["contributionDays"]:
            day = date.fromisoformat(raw["date"])
            if not start <= day <= end:
                continue  # GitHub may return padding days from partial weeks.
            count = raw["contributionCount"]
            if type(count) is not int or count < 0:
                raise ValueError("Invalid daily contribution count")
            if day in seen:
                raise ValueError("Duplicate contribution date")
            seen.add(day)
            days.append({"date": day.isoformat(), "count": count})
    days.sort(key=lambda day: day["date"])
    expected = (end - start).days + 1
    if len(days) != expected:
        raise ValueError(f"Incomplete calendar: expected {expected} days, got {len(days)}")
    total = sum(day["count"] for day in days)
    if total != calendar["totalContributions"]:
        raise ValueError("Daily counts do not match the API contribution total")
    return {"schema": 1, "source": "GitHub GraphQL contributionCalendar",
            "username": username, "from": start.isoformat(), "to": end.isoformat(),
            "total": total, "days": days}


def fetch_snapshot(username, token, end=None):
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing; configure the Actions secret")
    end = end or date.today()
    start = end - timedelta(days=364)
    variables = {"login": username, "from": f"{start}T00:00:00Z",
                 "to": f"{end}T23:59:59Z"}
    req = Request("https://api.github.com/graphql",
                  data=json.dumps({"query": QUERY, "variables": variables}).encode(),
                  headers={"Authorization": f"Bearer {token}",
                           "Content-Type": "application/json", "User-Agent": "commit-city"})
    try:
        with urlopen(req, timeout=45) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"GitHub API returned HTTP {error.code}") from None
    except URLError:
        raise RuntimeError("GitHub API could not be reached") from None
    if payload.get("errors"):
        raise RuntimeError("GitHub GraphQL rejected the query; check token permissions")
    user = payload.get("data", {}).get("user")
    if not user:
        raise RuntimeError("GitHub user or contribution calendar unavailable")
    return normalize_calendar(user["contributionsCollection"]["contributionCalendar"],
                              username, start, end)


def tier(count, thresholds=None):
    if count == 0:
        return 0
    return 1 + sum(count > bound for bound in (thresholds or CONFIG["thresholds"]))


def building_height(count):
    level = tier(count)
    return CONFIG["heights"][level - 1] if level else 0


def project(column, row):
    """30-degree isometric projection; earlier days precede later days row by row."""
    return 650 + (column - row) * 27, 340 + (column + row) * 27 / math.sqrt(3)


class Canvas:
    def __init__(self, vector=True, scale=1):
        self.scale = scale
        self.image = Image.new("RGB", (round(WIDTH * scale), round(HEIGHT * scale)), BG)
        self.draw = ImageDraw.Draw(self.image)
        # svgwrite's SVG 1.1 validator predates ARIA and data-* attributes.
        # XML structure and data attributes are validated in the test suite.
        self.svg = svgwrite.Drawing(size=(WIDTH, HEIGHT), viewBox=f"0 0 {WIDTH} {HEIGHT}", debug=False) if vector else None
        if self.svg:
            self.svg.set_desc(title="Commit City — PedroYuri14",
                              desc="Each dated plot is one day; building height encodes real contributions.")
            self.svg.attribs.update({"role": "img", "aria-label": "Commit City de PedroYuri14"})
        self.fonts = {}

    def points(self, points):
        return [(round(x * self.scale), round(y * self.scale)) for x, y in points]

    def polygon(self, points, fill, stroke=None, title=None, group=None):
        self.draw.polygon(self.points(points), fill=fill)
        if stroke:
            self.draw.line(self.points(points + [points[0]]), fill=stroke, width=max(1, round(self.scale)))
        if self.svg:
            shape = self.svg.polygon(points=points, fill=fill, stroke=stroke or "none", stroke_width=0.8)
            if title:
                shape.set_desc(title=title)
            (group if group is not None else self.svg).add(shape)

    def line(self, points, color, width=1):
        self.draw.line(self.points(points), fill=color, width=max(1, round(width * self.scale)))
        if self.svg:
            self.svg.add(self.svg.polyline(points=points, fill="none", stroke=color, stroke_width=width))

    def rect(self, x, y, width, height, fill, radius=0):
        bounds = (round(x*self.scale), round(y*self.scale), round((x+width)*self.scale), round((y+height)*self.scale))
        self.draw.rounded_rectangle(bounds, round(radius*self.scale), fill=fill)
        if self.svg:
            self.svg.add(self.svg.rect((x, y), (width, height), rx=radius, fill=fill))

    def text(self, x, y, value, size=20, color=TEXT):
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(str(FONT), max(1, round(size*self.scale)))
        self.draw.text((round(x*self.scale), round(y*self.scale)), value,
                       font=self.fonts[size], fill=color, anchor="lt")
        if self.svg:
            self.svg.add(self.svg.text(value, insert=(x, y + size), fill=color,
                                      font_family="monospace", font_size=size))


def diamond(x, y, half=24):
    vertical = half / math.sqrt(3)
    return [(x, y - vertical), (x + half, y), (x, y + vertical), (x - half, y)]


def draw_building(canvas, x, y, height, level, label, index, lit=True, vector_group=None):
    half, depth = 19, 19 / math.sqrt(3)
    colors = {
        1: ("#315B8D", "#223E60", BLUE),
        2: ("#236D47", "#194A33", GREEN),
        3: ("#65508B", "#403259", PURPLE),
        4: ("#3B5F98", "#293F68", "#8EBEFF"),
    }
    left, right, roof = colors[level]
    # Restrained shadow stays on the street/plot, never represents another day.
    canvas.polygon([(x-half, y), (x+half, y), (x+half+19, y+18), (x+3, y+depth+18)], "#0B111A")
    canvas.polygon([(x-half, y), (x, y+depth), (x, y+depth-height), (x-half, y-height)], left, group=vector_group)
    canvas.polygon([(x, y+depth), (x+half, y), (x+half, y-height), (x, y+depth-height)], right, group=vector_group)
    canvas.polygon(diamond(x, y-height, half), roof, title=label, group=vector_group)
    canvas.polygon(diamond(x, y-height-1, 12), left, group=vector_group)
    # Window geometry follows the two visible isometric faces.
    for floor in range(8, max(8, int(height)-8), 13):
        for side in (-1, 1):
            for column in (5, 12):
                wx = x + side * column
                wy = y + depth - column / math.sqrt(3) - floor
                light = (index + floor + column + side) % 4 != 0
                color = "#B8DCC8" if lit and light else "#182A3D"
                window = [(wx, wy), (wx+side*3, wy-3/math.sqrt(3)),
                          (wx+side*3, wy-5-3/math.sqrt(3)), (wx, wy-5)]
                canvas.polygon(window, color, group=vector_group)


def render_scene(snapshot, t=None, vector=True, scale=1):
    canvas = Canvas(vector=vector, scale=scale)
    canvas.rect(24, 24, WIDTH-48, HEIGHT-48, SURFACE, 20)
    canvas.text(70, 62, "COMMIT CITY", 34)
    canvas.text(70, 112, "PedroYuri14 / contribuição por dia / últimos 365 dias", 18, MUTED)
    canvas.text(1085, 67, f"{snapshot['total']:>6} contribuições", 22, BLUE)
    active = sum(day["count"] > 0 for day in snapshot["days"])
    canvas.text(1122, 112, f"{active} dias ativos", 18, MUTED)
    canvas.line([(70, 161), (1530, 161)], "#30363D")
    canvas.text(70, 181, f"{snapshot['from']}  →  {snapshot['to']}", 17, MUTED)
    canvas.text(1065, 181, "ordem cronológica → por fileira", 16, MUTED)
    columns = CONFIG["columns"]
    days = snapshot["days"]
    positions = []
    # Draw the complete ground first. Days with zero remain empty plots.
    for index, day in enumerate(days):
        row, column = divmod(index, columns)
        x, y = project(column, row)
        pan = 0 if t is None else 8 * math.sin(2 * math.pi * t / CONFIG["duration_seconds"])
        x += pan
        label = f"{day['date']}: {day['count']} contribuições"
        canvas.polygon(diamond(x, y), "#1B2531", "#354154", label)
        # Circuit markings are grounds, not buildings or activity.
        if day["count"] == 0:
            canvas.line([(x-8, y), (x, y+4.6), (x+7, y+.6)], "#283748")
        positions.append((index, day, x, y, column+row))
    # Painter's order: buildings at the back precede buildings at the front.
    for index, day, x, y, _ in sorted(positions, key=lambda item: (item[4], item[2])):
        count = day["count"]
        if count == 0:
            continue
        growth = 1.0
        if t is not None:
            start = 1.5 + (index / max(1, len(days)-1)) * 3.4
            growth = max(0, min(1, (t-start)/1.1))
            growth = 1 - (1-growth)**3
            # Gradual reverse near the end; the loop joins at empty ground.
            duration = CONFIG["duration_seconds"]
            if t > duration-1.2:
                growth *= max(0, (duration-t)/1.2)**2
        if growth < .015:
            continue
        group = None
        if canvas.svg:
            group = canvas.svg.g(id=f"day-{day['date']}")
            group.attribs.update({"data-date": day["date"], "data-contributions": str(count)})
            group.set_desc(title=f"{day['date']}: {count} contribuições")
            canvas.svg.add(group)
        draw_building(canvas, x, y, building_height(count)*growth, tier(count),
                      f"{day['date']}: {count} contribuições", index,
                      lit=t is None or t >= 6.1, vector_group=group)
    canvas.line([(70, 986), (1530, 986)], "#30363D")
    a, b, c = CONFIG["thresholds"]
    labels = ["0 / vazio", f"1–{a} / pequena", f"{a+1}–{b} / médio",
              f"{b+1}–{c} / alto", f"{c+1}+ / arranha-céu"]
    for index, (label, color) in enumerate(zip(labels, ["#354154", BLUE, GREEN, PURPLE, "#8EBEFF"])):
        x = 72 + index*285
        canvas.rect(x, 1010, 10, 10, color, 2)
        canvas.text(x+21, 1003, label, 16, MUTED)
    return canvas


def validate_snapshot(snapshot):
    start, end = date.fromisoformat(snapshot["from"]), date.fromisoformat(snapshot["to"])
    calendar = {"totalContributions": snapshot["total"], "weeks": [
        {"contributionDays": [{"date": day["date"], "contributionCount": day["count"]}
                              for day in snapshot["days"]]}]}
    return normalize_calendar(calendar, snapshot["username"], start, end)


def generate(snapshot, destination, animate=True):
    snapshot = validate_snapshot(snapshot)
    destination = Path(destination)
    static = render_scene(snapshot)
    outputs = {"commit-city.svg": static.svg.tostring() + "\n"}
    png = io.BytesIO()
    static.image.save(png, format="PNG", optimize=True)
    outputs["commit-city-preview.png"] = png.getvalue()
    outputs["commit-city-data.json"] = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if animate:
        # 100 ms frame cadence; shared palette prevents flashing/dither noise.
        palette = static.image.resize((800, 540)).quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        frames = []
        fps, duration = CONFIG["fps"], CONFIG["duration_seconds"]
        for index in range(fps*duration):
            frame = render_scene(snapshot, t=index/fps, vector=False, scale=.75).image
            frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
        gif = io.BytesIO()
        frames[0].save(gif, format="GIF", save_all=True, append_images=frames[1:],
                       loop=0, duration=1000//fps, optimize=True, disposal=1)
        outputs["commit-city.gif"] = gif.getvalue()
    changed = [name for name, content in outputs.items() if write_changed(destination/name, content)]
    digest = hashlib.sha256(outputs["commit-city-data.json"].encode()).hexdigest()[:12]
    print(f"Real calendar: {snapshot['total']} contributions / {len(snapshot['days'])} days / data {digest}")
    print("Changed assets: " + (", ".join(changed) or "none"))
    return changed


def placeholder(destination):
    canvas = Canvas()
    canvas.rect(24, 24, WIDTH-48, HEIGHT-48, SURFACE, 20)
    canvas.text(80, 100, "COMMIT CITY", 38)
    canvas.text(80, 220, "Dados de contribuições indisponíveis", 28, PURPLE)
    canvas.text(80, 290, "Configure o token e execute novamente o workflow.", 22, MUTED)
    canvas.text(80, 340, "Nenhuma contribuição foi inventada.", 22, MUTED)
    write_changed(Path(destination)/"commit-city.svg", canvas.svg.tostring())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Real snapshot or fixture (tests only)")
    parser.add_argument("--output", type=Path, default=ROOT/"assets")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.input.read_text(encoding="utf-8")) if args.input else fetch_snapshot(
            os.environ.get("PROFILE_USERNAME", "PedroYuri14"), os.environ.get("GITHUB_TOKEN", ""))
        generate(snapshot, args.output, animate=not args.static_only)
    except (RuntimeError, ValueError, KeyError) as error:
        if not (args.output/"commit-city-data.json").exists():
            placeholder(args.output)
        print(f"Commit City error: {error}. Existing real data retained when available.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
