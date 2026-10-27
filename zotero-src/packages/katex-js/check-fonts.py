#!/usr/bin/python3
"""Check generated KaTeX font coverage, outlines and webfont conversions."""

from pathlib import Path
import sys
from fontTools.ttLib import TTFont

root = Path(sys.argv[1])
files = sorted(root.glob("KaTeX_*.ttf"))
assert len(files) == 20
for filename in files:
    font = TTFont(filename)
    cmap = font.getBestCmap()
    assert len(cmap) >= 20, filename
    assert font["head"].unitsPerEm == 1000, filename
    assert sum(font["glyf"][name].numberOfContours != 0 for name in cmap.values()) > 10, filename
    for extension in ("woff", "woff2"):
        converted = TTFont(filename.with_suffix("." + extension))
        assert converted.getBestCmap() == cmap, filename
        assert converted["hmtx"].metrics == font["hmtx"].metrics, filename
    if filename.name == "KaTeX_Main-Regular.ttf":
        assert {ord("H"), ord("o"), 0x221A}.issubset(cmap)
        assert font["hmtx"][cmap[ord("H")]][0] == 750
print("KaTeX: 20 font families, nonempty outlines, coverage and webfont conversions passed")
