#!/usr/bin/env python3
"""Helpers that build .drawio XML. Import this from a short generator script.

Example:
    import sys; sys.path.insert(0, "<skill dir>/scripts")
    from drawio_lib import Diagram
    d = Diagram()
    p = d.page("Architecture", 1600, 900, layers=["1 Network and services", "2 Traffic flow"])
    p.group("vpc", "VPC", "vpc", 200, 120, 800, 600)
    p.icon("alb", "Load balancer", "application_load_balancer", 300, 300)
    p.icon("eks", "EKS", "eks", 500, 300, resource=True)
    p.edge("e1", "alb", "eks", kind="public")
    d.save("diagram/architecture.drawio")
"""
from xml.sax.saxutils import quoteattr

FONT = "fontFamily=Helvetica;"
GROUPS = {  # kind: (shape, stroke colour, dashed)
    "cloud": ("mxgraph.aws4.group_aws_cloud_alt", "#232F3E", False),
    "region": ("mxgraph.aws4.group_region", "#147EBA", True),
    "vpc": ("mxgraph.aws4.group_vpc2", "#248814", False),
    "az": ("mxgraph.aws4.group_availability_zone", "#545B64", True),
    "public_subnet": ("mxgraph.aws4.group_security_group", "#7AA116", False),
    "private_subnet": ("mxgraph.aws4.group_security_group", "#00A4A6", False),
    "asg": ("mxgraph.aws4.group_auto_scaling_group", "#D86613", True),
    "generic": ("rounded=0", "#545B64", True),
}
EDGE_COLOURS = {"public": "#E8590C", "private": "#2E7D32", "neutral": "#545B64"}
# Icon fill by AWS category. Unknown shapes fall back to dark grey.
ICON_FILL = {
    "ec2": "#ED7100", "eks": "#ED7100", "ecr": "#ED7100", "auto_scaling2": "#ED7100",
    "route_53": "#8C4FFF", "api_gateway": "#E7157B", "vpc_privatelink": "#8C4FFF",
    "cloud_map": "#E7157B", "aurora": "#C925D1", "waf": "#DD344C",
    "secrets_manager": "#DD344C", "identity_and_access_management": "#DD344C",
    "key_management_service": "#DD344C", "cloudwatch_2": "#E7157B", "client": "#232F3D",
}


def _attr(v):
    return quoteattr(str(v))


class Page:
    def __init__(self, name, width, height, layers, index):
        self.name, self.width, self.height, self.index = name, width, height, index
        # Minimum readable text: 22 px on 1920x1080 slides, 14 px on overview pages.
        self.base_font = 22 if (width, height) == (1920, 1080) else 14
        self.cells, self.ids = [], set()
        self.layer_ids = []
        for i, lname in enumerate(layers or ["Layer 1"], 1):
            lid = f"p{index}-layer-{i}"
            self.layer_ids.append(lid)
            self._add(f'<mxCell id="{lid}" value={_attr(lname)} parent="0"/>', lid)
        self.default_parent = self.layer_ids[0]

    def _add(self, xml, cid):
        if cid in self.ids:
            raise ValueError(f"duplicate cell id on page {self.name!r}: {cid}")
        self.ids.add(cid)
        self.cells.append(xml)

    def _parent(self, layer):
        return self.layer_ids[layer - 1] if layer else self.default_parent

    def group(self, cid, label, kind, x, y, w, h, layer=None, fill=False):
        shape, stroke, dashed = GROUPS[kind]
        fill_c = "fillColor=#FFFFFF;" if fill else "fillColor=none;"
        style = (f"{'shape=' if shape.startswith('mxgraph') else ''}{shape};{fill_c}"
                 f"strokeColor={stroke};fontColor={stroke};{'dashed=1;' if dashed else ''}"
                 f"verticalAlign=top;align=left;spacingLeft=30;container=0;{FONT}fontSize={self.base_font};")
        self._add(f'<mxCell id="{cid}" value={_attr(label)} style="{style}" vertex="1" parent="{self._parent(layer)}">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>', cid)

    def icon(self, cid, label, shape, x, y, size=48, resource=False, label_pos="bottom",
             faded=False, layer=None, font_size=None):
        pos = {"bottom": "verticalLabelPosition=bottom;verticalAlign=top;align=center;",
               "right": "labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;spacingLeft=6;",
               "left": "labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;spacingRight=6;",
               "top": "verticalLabelPosition=top;verticalAlign=bottom;align=center;"}[label_pos]
        if shape.startswith("mxgraph."):
            core = f"shape={shape};"
        elif resource:
            core = (f"shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{shape};"
                    f"fillColor={ICON_FILL.get(shape, '#232F3D')};strokeColor=#ffffff;")
        else:
            core = f"shape=mxgraph.aws4.{shape};fillColor={ICON_FILL.get(shape, '#232F3D')};"
        font_size = font_size or self.base_font
        style = f"{core}{pos}{FONT}fontSize={font_size};{'opacity=35;' if faded else ''}"
        self._add(f'<mxCell id="{cid}" value={_attr(label)} style="{style}" vertex="1" parent="{self._parent(layer)}">'
                  f'<mxGeometry x="{x}" y="{y}" width="{size}" height="{size}" as="geometry"/></mxCell>', cid)

    def text(self, cid, label, x, y, w=300, h=40, size=None, bold=False, layer=None):
        size = size or self.base_font
        style = f"text;html=0;align=left;verticalAlign=middle;{FONT}fontSize={size};{'fontStyle=1;' if bold else ''}"
        self._add(f'<mxCell id="{cid}" value={_attr(label)} style="{style}" vertex="1" parent="{self._parent(layer)}">'
                  f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>', cid)

    def badge(self, cid, number, x, y, size=40, layer=None):
        style = (f"ellipse;fillColor=#007CBD;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;"
                 f"{FONT}fontSize={max(16, self.base_font)};aspect=fixed;")
        self._add(f'<mxCell id="{cid}" value="{number}" style="{style}" vertex="1" parent="{self._parent(layer)}">'
                  f'<mxGeometry x="{x}" y="{y}" width="{size}" height="{size}" as="geometry"/></mxCell>', cid)

    def edge(self, cid, source, target, kind="neutral", dashed=False, label=None,
             label_pos=0.0, width=3, layer=None, points=None):
        if source not in self.ids or target not in self.ids:
            raise ValueError(f"edge {cid}: source or target not defined yet ({source} -> {target})")
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=open;endFill=0;"
                 f"strokeWidth={width};strokeColor={EDGE_COLOURS[kind]};{'dashed=1;' if dashed else ''}"
                 f"{FONT}fontSize={self.base_font};")
        pts = ""
        if points:
            pts = '<Array as="points">' + "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points) + "</Array>"
        label_geo = f'<mxGeometry x="{label_pos}" relative="1" as="geometry">{pts}</mxGeometry>'
        self._add(f'<mxCell id="{cid}" value={_attr(label or "")} style="{style}" edge="1" '
                  f'parent="{self._parent(layer)}" source="{source}" target="{target}">{label_geo}</mxCell>', cid)

    def legend(self, x, y, layer=None, prefix="legend"):
        """Small legend for the three arrow colours."""
        rows = [("public", "Public traffic"), ("private", "Private traffic"), ("neutral", "Other / optional (dashed)")]
        self.text(f"{prefix}-title", "Legend", x, y, 260, 30, self.base_font + 2, True, layer)
        for i, (kind, label) in enumerate(rows):
            yy = y + 40 + i * 40
            a, b = f"{prefix}-a{i}", f"{prefix}-b{i}"
            for cid, xx in ((a, x), (b, x + 60)):
                self._add(f'<mxCell id="{cid}" value="" style="ellipse;fillColor=none;strokeColor=none;" vertex="1" '
                          f'parent="{self._parent(layer)}"><mxGeometry x="{xx}" y="{yy}" width="2" height="2" '
                          f'as="geometry"/></mxCell>', cid)
            self.edge(f"{prefix}-e{i}", a, b, kind, dashed=(kind == "neutral"), width=3, layer=layer)
            self.text(f"{prefix}-t{i}", label, x + 80, yy - 14, 360, 28, self.base_font, False, layer)

    def xml(self):
        body = "\n        ".join(self.cells)
        return (f'  <diagram name={_attr(self.name)} id="page-{self.index}">\n'
                f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" '
                f'arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.width}" pageHeight="{self.height}" '
                f'math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n        {body}\n      </root>\n'
                f'    </mxGraphModel>\n  </diagram>\n')


class Diagram:
    def __init__(self):
        self.pages = []

    def page(self, name, width=1600, height=900, layers=None):
        p = Page(name, width, height, layers, len(self.pages) + 1)
        self.pages.append(p)
        return p

    def slide(self, name, layers=None):
        """A 1920x1080 slide page."""
        return self.page(name, 1920, 1080, layers)

    def to_xml(self):
        return '<mxfile host="archsmith">\n' + "".join(p.xml() for p in self.pages) + "</mxfile>\n"

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_xml())
        return path
