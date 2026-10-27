#!/usr/bin/python3
"""Check source-built Codicons codepoints, outlines, and font metrics."""

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont


def check(filename):
    inputs = json.loads(filename.with_suffix(".inputs.json").read_text())
    with TTFont(filename) as font:
        mapping = font.getBestCmap()
        assert set(mapping) == {int(value) for value in inputs["glyphs"]}
        assert len(mapping) > 400
        assert font["head"].unitsPerEm == 300
        assert font["hhea"].ascent == 300 and font["hhea"].descent == 0
        for codepoint, name in mapping.items():
            glyph = font["glyf"][name]
            assert glyph.numberOfContours > 0, f"Empty source glyph: {codepoint:#x}"
            assert font["hmtx"][name][0] == 300
            # The upstream converter's integer quadratic approximation permits
            # small curve overshoots, also present in the original font.
            assert -3 <= glyph.xMin <= glyph.xMax <= 303
            assert -3 <= glyph.yMin <= glyph.yMax <= 303
        assert 0xea60 in mapping  # Add
        assert 0xec1d in mapping  # The pinned editor's git-fetch registration
    print(f"Codicons: {len(mapping)} original-artwork glyphs, source codepoints and metrics passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", type=Path)
    check(parser.parse_args().font)
