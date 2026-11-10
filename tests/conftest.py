"""Build small .docx fixtures in code, so tests never need the (private) corpus."""
from __future__ import annotations

import pytest
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from src.rag.ingest import load_docx


class DocBuilder:
    def __init__(self):
        self.doc = Document()

    def title(self, text):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(text).bold = True
        return self

    def head(self, text, centered=False):
        p = self.doc.add_paragraph()
        if centered:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(text).bold = True
        return self

    def para(self, text, bold_prefix=None):
        p = self.doc.add_paragraph()
        if bold_prefix:
            p.add_run(bold_prefix).bold = True
        p.add_run(text)
        return self

    def table(self, rows, header_rows=1, merges=(), bottom=()):
        """rows: list of lists of str ('\\n' = new paragraph in the cell);
        merges: ((r1, c1), (r2, c2)) pairs; bottom: cells to align at the bottom."""
        t = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if v is None:
                    continue
                cell = t.cell(r, c)
                parts = v.split("\n")
                cell.paragraphs[0].add_run(parts[0])
                for x in parts[1:]:
                    cell.add_paragraph(x)
        for r in range(header_rows):
            trpr = t.rows[r]._tr.get_or_add_trPr()
            h = OxmlElement("w:tblHeader")
            h.set(qn("w:val"), "true")
            trpr.append(h)
        for (a, b) in merges:
            t.cell(*a).merge(t.cell(*b))
        for (r, c) in bottom:
            tcpr = t.cell(r, c)._tc.get_or_add_tcPr()
            va = OxmlElement("w:vAlign")
            va.set(qn("w:val"), "bottom")
            tcpr.append(va)
        return self

    def build(self, tmp_path, doc_id="test", title="Văn bản thử"):
        path = tmp_path / f"{doc_id}.docx"
        self.doc.save(path)
        return load_docx(path, doc_id, title)


@pytest.fixture
def builder():
    return DocBuilder()
