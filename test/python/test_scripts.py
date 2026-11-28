"""Fixture tests for the skill scripts. Standard library only: python3 -m unittest discover -s test/python"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS = os.path.join(ROOT, "skills", "archsmith", "scripts")
FIXTURES = os.path.join(ROOT, "test", "fixtures")
sys.path.insert(0, SCRIPTS)

import drawio_lib  # noqa: E402
import tf_summary  # noqa: E402
import validate  # noqa: E402


def wrap(cells, w=1600, h=900, name="Page"):
    return ('<mxfile><diagram name="%s" id="d"><mxGraphModel pageWidth="%d" pageHeight="%d"><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>%s</root></mxGraphModel></diagram></mxfile>' % (name, w, h, cells))


def vertex(cid, style, value="Item", x=0, y=0, w=48, h=48):
    return ('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>' % (cid, value, style, x, y, w, h))


class ValidateCase(unittest.TestCase):
    def check_xml(self, xml):
        with tempfile.NamedTemporaryFile("w", suffix=".drawio", delete=False, encoding="utf-8") as f:
            f.write(xml)
        self.addCleanup(os.unlink, f.name)
        return validate.check(f.name)

    def run_main(self, xml, *flags):
        with tempfile.NamedTemporaryFile("w", suffix=".drawio", delete=False, encoding="utf-8") as f:
            f.write(xml)
        self.addCleanup(os.unlink, f.name)
        with contextlib.redirect_stdout(io.StringIO()):
            return validate.main(["validate.py", f.name, *flags])

    def test_clean_diagram_has_no_findings(self):
        d = drawio_lib.Diagram()
        p = d.page("Architecture", layers=["1 Network"])
        p.group("vpc", "VPC", "vpc", 100, 100, 700, 500)
        p.icon("alb", "Load balancer", "application_load_balancer", 200, 300)
        p.icon("eks", "EKS", "eks", 500, 300, resource=True)
        p.edge("e1", "alb", "eks", kind="public")
        p.legend(900, 100)
        s = d.slide("Slide")
        s.icon("a", "App", "ec2", 200, 300, resource=True)
        s.icon("b", "Database", "aurora", 700, 300, resource=True)
        s.edge("e", "a", "b", kind="private")
        with tempfile.TemporaryDirectory() as tmp:
            path = d.save(os.path.join(tmp, "sub", "a.drawio"))
            errors, warnings = validate.check(path)
        self.assertEqual((errors, warnings), ([], []))

    def test_invalid_xml_is_an_error(self):
        errors, _ = self.check_xml("<mxfile><diagram>")
        self.assertTrue(errors and "does not parse" in errors[0])

    def test_compressed_page_is_an_error(self):
        errors, _ = self.check_xml('<mxfile><diagram name="x">eJzLSM3JyVcozy/KSQEAGgsEXQ==</diagram></mxfile>')
        self.assertTrue(any("compressed" in e for e in errors))

    def test_duplicate_ids_and_missing_edge_target(self):
        xml = wrap(vertex("a", "shape=mxgraph.aws4.bucket;") + vertex("a", "shape=mxgraph.aws4.bucket;", x=200)
                   + '<mxCell id="e" edge="1" parent="1" source="a" target="ghost"><mxGeometry relative="1" as="geometry"/></mxCell>')
        errors, _ = self.check_xml(xml)
        self.assertTrue(any("duplicate cell id: a" in e for e in errors))
        self.assertTrue(any("target ghost does not exist" in e for e in errors))

    def test_image_url_is_an_error(self):
        errors, _ = self.check_xml(wrap(vertex("a", "shape=image;image=https://example.com/x.png;")))
        self.assertTrue(any("image URL" in e for e in errors))

    def test_small_text_warns_on_slide_but_not_at_floor(self):
        small = vertex("a", "shape=mxgraph.aws4.bucket;fontSize=16;")
        _, warnings = self.check_xml(wrap(small, 1920, 1080))
        self.assertTrue(any("under 20px" in w for w in warnings))
        _, warnings = self.check_xml(wrap(small, 1600, 900))
        self.assertFalse(any("text under" in w for w in warnings))

    def test_overlap_and_oversized_canvas_warn(self):
        xml = wrap(vertex("a", "shape=mxgraph.aws4.bucket;fontSize=14;", x=100, y=100)
                   + vertex("b", "shape=mxgraph.aws4.bucket;fontSize=14;", x=110, y=110), 3200, 900)
        _, warnings = self.check_xml(xml)
        self.assertTrue(any("likely overlaps" in w for w in warnings))
        self.assertTrue(any("too big to view" in w for w in warnings))

    def test_shape_allowlist(self):
        _, ok = self.check_xml(wrap(vertex("a", "shape=mxgraph.aws4.bucket;fontSize=14;")))
        self.assertFalse(any("aws4_shapes.txt" in w for w in ok))
        _, bad = self.check_xml(wrap(vertex("a", "shape=mxgraph.aws4.made_up_shape;fontSize=14;")))
        self.assertTrue(any("made_up_shape" in w for w in bad))
        _, res = self.check_xml(wrap(vertex("a", "shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.not_real;fontSize=14;")))
        self.assertTrue(any("not_real" in w for w in res))

    def test_other_shape_library_warns(self):
        _, warnings = self.check_xml(wrap(vertex("a", "shape=mxgraph.kubernetes.pod;fontSize=14;")))
        self.assertTrue(any("kubernetes" in w for w in warnings))

    def test_exit_codes(self):
        clean = wrap(vertex("a", "shape=mxgraph.aws4.bucket;fontSize=14;"))
        warn = wrap(vertex("a", "shape=mxgraph.aws4.made_up_shape;fontSize=14;"))
        self.assertEqual(self.run_main(clean, "--strict"), 0)
        self.assertEqual(self.run_main(warn), 0)
        self.assertEqual(self.run_main(warn, "--strict"), 1)
        self.assertEqual(self.run_main("<mxfile><diagram>"), 1)

    def test_allowlist_covers_every_shape_in_shapes_md(self):
        allowed = validate.load_allowlist()
        self.assertTrue(allowed)
        for shape in ("route_53", "eks", "application_load_balancer", "group_vpc2", "container_3", "authenticated_user"):
            self.assertIn(shape, allowed)
        for _, (shape, _, _) in drawio_lib.GROUPS.items():
            if shape.startswith("mxgraph.aws4."):
                self.assertIn(shape.split(".")[-1], allowed)


class LibCase(unittest.TestCase):
    def test_duplicate_id_raises(self):
        p = drawio_lib.Diagram().page("P")
        p.icon("a", "A", "ec2", 0, 0)
        with self.assertRaises(ValueError):
            p.icon("a", "B", "ec2", 100, 0)

    def test_edge_needs_defined_cells(self):
        p = drawio_lib.Diagram().page("P")
        p.icon("a", "A", "ec2", 0, 0)
        with self.assertRaises(ValueError):
            p.edge("e", "a", "missing")

    def test_font_floor_by_page_size(self):
        d = drawio_lib.Diagram()
        self.assertEqual(d.slide("S").base_font, 22)
        self.assertEqual(d.page("O").base_font, 14)

    def test_labels_are_escaped(self):
        d = drawio_lib.Diagram()
        d.page("P").icon("a", 'A "quoted" & <tag>', "ec2", 0, 0)
        import xml.etree.ElementTree as ET
        ET.fromstring(d.to_xml())


class TfSummaryCase(unittest.TestCase):
    def test_scan_dirs(self):
        res, mods, cidrs, az_files = tf_summary.scan_dirs([os.path.join(FIXTURES, "tf")])
        self.assertEqual(sorted(res), ["aws_eks_cluster", "aws_subnet", "aws_vpc"])
        self.assertEqual(len(res["aws_subnet"]), 2)
        self.assertEqual(mods, [("vpc", "terraform-aws-modules/vpc/aws")])
        self.assertEqual(set(cidrs), {"10.0.0.0/16", "10.0.1.0/24", "10.0.2.0/24"})
        self.assertEqual(az_files, {"main.tf"})

    def test_scan_plan(self):
        res = tf_summary.scan_plan(os.path.join(FIXTURES, "plan.json"))
        self.assertEqual(res["aws_vpc"], ["aws_vpc.main"])
        self.assertEqual(res["aws_lambda_function"], ["module.app.aws_lambda_function.fn"])

    def test_plan_fixture_is_valid_json(self):
        with open(os.path.join(FIXTURES, "plan.json"), encoding="utf-8") as f:
            json.load(f)


if __name__ == "__main__":
    unittest.main()
