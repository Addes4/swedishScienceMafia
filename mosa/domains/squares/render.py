"""Packings as SVG in the style of the squares-in-squares catalogue (grey squares, hairline edges, y axis up)."""
from __future__ import annotations

import math


def catalogue_svg(poses, side, comment=""):
    uses = [f'        <use xlink:href="#one" transform="translate({float(x)!r} {side-float(y)!r}) rotate({-math.degrees(a)!r}) '
            f'translate(-0.5 -0.5)"/>' for x, y, a in poses]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!--
{comment}
-->
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [
    <!ENTITY  s "{side!r}">
    <!ENTITY hs  "{side/2!r}">
]>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%" viewBox="-&hs; -&hs; &s; &s;" style="fill:#B2B2B2; stroke:black; stroke-width:0.002" id="svg">
    <defs>
        <rect width="&s;" height="&s;" id="outer" x="-&hs;" y="-&hs;"/>
        <rect width="1"   height="1"   id="one"/>
    </defs>
    <use xlink:href="#outer" style="fill:white; stroke:none"/>
    <g transform="translate(-&hs; -&hs;)">
{chr(10).join(uses)}
    </g>
    <use xlink:href="#outer" style="fill:none"/>
</svg>
'''
