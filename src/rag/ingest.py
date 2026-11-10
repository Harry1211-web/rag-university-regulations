"""Step 2 - Read a .docx regulation into an ordered list of blocks.

The corpus is Word files (most were re-typed from scans), so we read paragraphs AND tables
in document order with python-docx instead of extracting text from PDF pages.

Output blocks:
- Para:  one paragraph, NFC-normalised, plus the formatting signals the chunker needs to
         recognise headings (bold ratio, centred, italic).
- Table: the cell grid with merged cells resolved, and how many rows are header rows.

There are no page numbers in a .docx, so citations point to the article/section instead
(e.g. "Điều 25 khoản 2"), which is also what a student would quote.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph

_WS = re.compile(r"[ \t ​]+")


def normalize(text: str) -> str:
    """NFC + collapse spaces. The same Vietnamese letter can be stored as one code point
    (NFC) or as base letter + combining marks (NFD); without this, BM25 and exact matching
    silently miss words typed on a different keyboard/OS."""
    text = unicodedata.normalize("NFC", text)
    lines = [_WS.sub(" ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


@dataclass
class Para:
    text: str
    bold: float = 0.0      # share of visible characters that are bold
    italic: float = 0.0
    centered: bool = False
    kind: str = "para"


@dataclass
class Cell:
    text: str
    key: int               # identity of the underlying <w:tc>; equal keys = one merged cell
    bold: float = 0.0
    lines: list[str] = field(default_factory=list)  # one entry per paragraph, blanks KEPT
    valign: str = "top"    # "bottom" cells align their lines with the LAST lines of a sibling cell
    # (blank lines matter: some cells align "Lần 1 / Lần 2" with the lines of another cell)


@dataclass
class Table:
    rows: list[list[Cell]]
    n_header: int = 1
    kind: str = "table"
    caption: str = ""      # filled later by the chunker (preceding "Bảng ..." line)
    legend: str = ""       # filled later (paragraph right before the table that explains codes)

    @property
    def n_cols(self) -> int:
        return max((len(r) for r in self.rows), default=0)


@dataclass
class DocBlocks:
    doc_id: str
    title: str
    path: str
    blocks: list = field(default_factory=list)


def _para(p: DocxParagraph) -> Para | None:
    text = normalize(p.text)
    if not text:
        return None
    n = bold = ital = 0
    for r in p.runs:
        k = len(r.text.strip())
        n += k
        if r.bold or (r.bold is None and p.style is not None and p.style.font.bold):
            bold += k
        if r.italic:
            ital += k
    al = p.alignment if p.alignment is not None else p.paragraph_format.alignment
    centered = al is not None and int(al) == 1  # WD_ALIGN_PARAGRAPH.CENTER
    return Para(text=text, bold=bold / n if n else 0.0, italic=ital / n if n else 0.0, centered=centered)


def _table(t: DocxTable) -> Table | None:
    rows: list[list[Cell]] = []
    n_header = 0
    keys: dict = {}   # <w:tc> element -> stable int; holding the elements keeps lxml proxies alive
    for i, row in enumerate(t.rows):
        trpr = row._tr.trPr
        if trpr is not None and trpr.find(qn("w:tblHeader")) is not None and i == n_header:
            n_header += 1
        # row.cells repeats a horizontally merged cell for every grid column it spans and
        # returns the top cell for vertically merged continuations -> one value per column.
        cells = []
        for c in row.cells:
            k = keys.setdefault(c._tc, len(keys))
            lines = [normalize(p.text) for p in c.paragraphs]
            while lines and not lines[-1]:
                lines.pop()
            n = b = 0
            for p in c.paragraphs:
                for r in p.runs:
                    m = len(r.text.strip())
                    n += m
                    b += m if r.bold else 0
            va = c._tc.tcPr.find(qn("w:vAlign")) if c._tc.tcPr is not None else None
            valign = va.get(qn("w:val")) if va is not None else "top"
            cells.append(Cell(normalize(c.text), k, b / n if n else 0.0, lines, valign))
        rows.append(cells)
    if not rows or not any(c.text for r in rows for c in r):
        return None
    return Table(rows=rows, n_header=max(n_header, 1))


def iter_blocks(doc) -> list:
    out = []
    body = doc.element.body
    for el in body.iterchildren():
        if el.tag == qn("w:p"):
            b = _para(DocxParagraph(el, doc))
        elif el.tag == qn("w:tbl"):
            b = _table(DocxTable(el, doc))
        else:
            b = None
        if b is not None:
            out.append(b)
    return out


def load_docx(path: str | Path, doc_id: str, title: str | None = None) -> DocBlocks:
    path = Path(path)
    doc = Document(str(path))
    return DocBlocks(doc_id=doc_id, title=title or normalize(path.stem), path=str(path), blocks=iter_blocks(doc))


def load_manifest(manifest: str | Path) -> list[dict]:
    import yaml

    with open(manifest, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_corpus(data_dir: str | Path, manifest: str | Path) -> list[DocBlocks]:
    data_dir = Path(data_dir)
    docs = []
    for m in load_manifest(manifest):
        p = data_dir / unicodedata.normalize("NFC", m["file"])
        if not p.exists():  # file names typed on Windows may be NFD on disk
            cands = [x for x in data_dir.iterdir() if unicodedata.normalize("NFC", x.name) == p.name]
            if not cands:
                raise FileNotFoundError(p)
            p = cands[0]
        docs.append(load_docx(p, m["id"], m.get("title")))
    return docs
