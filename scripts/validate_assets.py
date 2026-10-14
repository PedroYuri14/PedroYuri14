"""Validate production assets, displayed Java, README paths and real calendar data."""
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops
from generate_commit_city import validate_snapshot

ROOT = Path(__file__).resolve().parents[1]


def main():
    readme = (ROOT/"README.md").read_text(encoding="utf-8")
    assert not re.search(r"pok[eé]mon|commit-map|pokemon-walk", readme, re.I)
    refs = re.findall(r'(?:src|srcset)="(\./[^" ]+)"', readme)
    for path in refs:
        assert (ROOT/path).is_file(), f"Missing README image: {path}"
    for path in (ROOT/"assets").rglob("*.svg"):
        ET.parse(path)
    for name, expected in [("animated-java-ide.gif", (1600, 900)),
                           ("animated-java-ide-mobile.gif", (1188, 806)),
                           ("commit-city.gif", (1200, 810))]:
        path = ROOT/"assets"/name
        with Image.open(path) as gif:
            assert gif.size == expected, (name, gif.size)
            assert gif.is_animated and gif.n_frames > 20, name
            assert gif.info.get("loop") == 0, name
            duration = 0
            first = gif.convert("RGB")
            for frame in range(gif.n_frames):
                gif.seek(frame)
                duration += gif.info.get("duration", 0)
                gif.load()
            expected_duration = 12000 if name.startswith("commit-city") else 15000
            assert duration == expected_duration, (name, duration)
            assert path.stat().st_size < 10*1024*1024, f"GIF too large: {name}"
            if name == "animated-java-ide.gif":
                # Both ends dissolve to the same background; no discontinuous cut.
                difference = ImageChops.difference(first, gif.convert("RGB"))
                assert sum(difference.resize((1, 1)).getpixel((0, 0))) < 18
            print(f"{name}: {gif.size}, {gif.n_frames} frames, {duration/1000:g}s, {path.stat().st_size/1024/1024:.2f} MiB")
    html = (ROOT/"animations/java-ide/index.html").read_text(encoding="utf-8")
    displayed = re.search(r'<pre id="java-source" hidden>(.*?)</pre>', html, re.S).group(1)
    java = (ROOT/"animations/java-ide/src/dev/pedroyuri/Developer.java").read_text(encoding="utf-8")
    assert displayed.strip() == java.strip(), "Java animation source differs from compiled Java"
    snapshot = validate_snapshot(json.loads((ROOT/"assets/commit-city-data.json").read_text(encoding="utf-8")))
    assert snapshot["username"] == "PedroYuri14" and len(snapshot["days"]) == 365
    svg = ET.parse(ROOT/"assets/commit-city.svg").getroot()
    buildings = [node for node in svg.iter() if node.get("data-contributions")]
    actual = {node.get("data-date"): int(node.get("data-contributions")) for node in buildings}
    expected = {day["date"]: day["count"] for day in snapshot["days"] if day["count"]}
    assert actual == expected, "City buildings do not match the real contribution data"
    assert len(re.findall(r'assets/icons/', readme)) == 24
    print(f"Valid: {len(refs)} README image references, 24 logos, Java source, SVG XML and {len(actual)} real buildings.")


if __name__ == "__main__":
    main()
