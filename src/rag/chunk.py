"""Step 3 - Split regulations into retrieval chunks that each carry ONE meaningful unit.

Pipeline for one document (see README "Chunking" for the reasoning):

1. classify  - every paragraph becomes a heading (with a rank) or body text; leading title
               lines are dropped (the document title is added back as context).
2. sectionize - a new section starts at each heading. Documents with "Điều" (articles) are cut
               ONLY at Chương/Điều; anything deeper (khoản, bold sub-titles) stays inside the
               article. Other documents (guides, lists) are cut at every heading.
3. merge     - tiny sections (< min_words) are glued to their neighbour so a chunk is never just
               "Thông tin liên hệ: phòng A0009".
4. split     - long sections (> max_words) are packed greedily from "units": a khoản with its
               points a), b), - ... ; one table row; or, as a last resort, sentences.
5. render    - each chunk gets a context header (document > chapter > article / section) that is
               embedded together with the text, so the chunk still makes sense on its own.

Tables are turned into "Column: value" lines, one block per row, because most numeric answers
(grade scales, scholarship rates, exemption scores) live in tables.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, replace

from .ingest import DocBlocks, Para, Table

# --------------------------------------------------------------------------- headings
RANK_CHAPTER, RANK_LETTER, RANK_ARTICLE, RANK_NUM, RANK_NUM2, RANK_NUM3, RANK_LABEL = 1, 2, 3, 4, 5, 6, 7

RE_CHAPTER = re.compile(r"^(chương|phụ lục)\s+[ivxlc\d]+\b\.?", re.I)
RE_ROMAN = re.compile(r"^[IVX]+\.\s")
RE_ARTICLE = re.compile(r"^Điều\s+(\d+)\s*\.")
RE_LETTER = re.compile(r"^[A-Z]\.\s")
RE_NUM3 = re.compile(r"^\d+\.\d+\.\d+\.?\s")
RE_NUM2 = re.compile(r"^\d+\.\d+\.?\s")
RE_NUM = re.compile(r"^\d+\.\s")
RE_CAPTION = re.compile(r"^(bảng|danh mục)\b", re.I)
# start of a "unit" inside a section: khoản "1.", điểm "a)", "(1)", "Bước 1", "Trường hợp 1", bullets
RE_KHOAN = re.compile(r"^\d+\.\s")
RE_POINT = re.compile(r"^([a-zđ][\)\.]|\(\d+\)|[-+▪•]\s|Bước\s+\d|Trường hợp\s+\d|TH\d)", re.I)
RE_SENT = re.compile(r"(?<=[.;:!?])\s+(?=[A-ZĐÀ-Ỹ0-9(\-+])")


def is_caps(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= 3 and sum(c.isupper() for c in letters) / len(letters) > 0.9


def n_words(text: str) -> int:
    return len(text.split())


def heading_rank(p: Para) -> int | None:
    """Rank of a heading paragraph, or None for body text.
    A heading must be (almost) fully bold and short; 'Điều N.' is a heading whatever its style."""
    t = p.text
    if RE_ARTICLE.match(t) and len(t) < 300:
        return RANK_ARTICLE
    if p.bold < 0.85 or len(t) > 260:
        return None
    if RE_CHAPTER.match(t) or RE_ROMAN.match(t):
        return RANK_CHAPTER
    if RE_LETTER.match(t):
        return RANK_LETTER
    if RE_NUM3.match(t):
        return RANK_NUM3
    if RE_NUM2.match(t):
        return RANK_NUM2
    if RE_NUM.match(t):
        return RANK_NUM
    if p.centered and is_caps(t):
        return RANK_CHAPTER          # unnumbered centred title, e.g. "CÁC KHOA VÀ TRUNG TÂM"
    if t.endswith(":") or t.lstrip("▪•- ").endswith(":"):
        return RANK_LABEL            # e.g. "Thông tin liên hệ:", "▪ Đối với sinh viên năm thứ nhất:"
    if n_words(t) <= 25 and not t.endswith((".", ";")) and not RE_CAPTION.match(t):
        return RANK_LABEL            # e.g. "Nội dung 1. Học tập suốt đời để làm chủ tri thức ..."
    return None


# --------------------------------------------------------------------------- data classes
@dataclass
class Unit:
    """Smallest piece we never cut in the middle (unless it alone exceeds max_words)."""
    text: str
    kind: str = "para"            # para | row | heading
    khoan: str | None = None      # "2" when the unit is khoản 2 of an article
    table: str | None = None      # caption of the table the row belongs to
    first: bool = False           # first row of its table (so a chunk starting here is not "tiếp theo")
    sub: str | None = None        # inline sub-title above this unit ("▪ Đối với sinh viên năm thứ 2:")

    @property
    def words(self) -> int:
        return n_words(self.text)


@dataclass
class Section:
    path: list[str]               # heading texts from the top, e.g. ["Chương III. ...", "Điều 25. ..."]
    units: list[Unit] = field(default_factory=list)
    article: int | None = None

    @property
    def words(self) -> int:
        return sum(u.words for u in self.units)


@dataclass
class Chunk:
    id: str
    doc_id: str
    doc_title: str
    path: list[str]
    text: str
    context: str
    article: int | None = None
    khoan: list[str] = field(default_factory=list)
    part: tuple[int, int] = (1, 1)
    has_table: bool = False
    meta: dict = field(default_factory=dict)

    @property
    def embed_text(self) -> str:
        return f"{self.context}\n\n{self.text}"

    @property
    def n_words(self) -> int:
        return n_words(self.text)

    @property
    def loc(self) -> str:
        """Short human citation: 'Điều 25' / 'II > 2. Học bổng ...'"""
        if self.article is not None:
            k = f" khoản {', '.join(self.khoan)}" if self.khoan and self.part[1] > 1 else ""
            return f"Điều {self.article}{k}"
        return " > ".join(self.path[-2:]) if self.path else "(không có mục)"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "doc_id": self.doc_id, "doc_title": self.doc_title, "path": self.path,
            "loc": self.loc, "article": self.article, "khoan": self.khoan, "part": list(self.part),
            "has_table": self.has_table, "n_words": self.n_words, "context": self.context,
            "text": self.text, "sha1": hashlib.sha1(self.embed_text.encode()).hexdigest()[:12],
            **self.meta,
        }


# --------------------------------------------------------------------------- tables
_LEGEND = re.compile(r"\((\d+)\)\s*:\s*([^\-–(]+?)\s*(?=-|–|$|\.$)")


def _join_lines(v: str) -> str:
    """Multi-line cell -> one line: '; ' between items, but no ';' after a line ending in ':'."""
    out = ""
    for x in (x.strip().rstrip(";") for x in v.split("\n")):
        if not x:
            continue
        out += (" " if out.endswith(":") else "; " if out else "") + x
    return out


def parse_legend(text: str) -> dict[str, str]:
    """'(1): Nhắc nhở - (2): Phê bình - ...' -> {'(1)': 'Nhắc nhở', ...}"""
    found = {f"({k})": v.strip().rstrip(".") for k, v in _LEGEND.findall(text)}
    return found if len(found) >= 3 else {}


SKIP_COLS = {"tt", "stt"}


def _header_names(t: Table, legend: dict[str, str]) -> tuple[list[str], list[str | None]]:
    """Per column: (leaf header name, group header or None).
    With two header rows, a top cell spanning several columns becomes the group header and the
    bottom cell the leaf name ("Aptis ESOL" > "General"). Codes like "(5)" are expanded with the
    legend found right before the table ("(5) Cảnh cáo")."""
    n = t.n_cols
    head = t.rows[: t.n_header]
    names, groups = [], []
    for j in range(n):
        col = [r[j] for r in head if j < len(r)]
        top = col[0]
        spans = sum(1 for c in head[0] if c.key == top.key) > 1
        leaf = next((c.text for c in reversed(col) if c.text), "")
        group = top.text if (len(col) > 1 and spans and top.text and top.text != leaf) else None
        if leaf in legend:
            leaf = f"{leaf} {legend[leaf]}"
        names.append(leaf.replace("\n", " "))
        groups.append(group.replace("\n", " ") if group else None)
    return names, groups


def _expand_aligned(row) -> list[list[str]] | None:
    """Row 28 of the violations table puts one sub-case per line in the label cell and aligns
    'Lần 1/Lần 2' with those lines in bottom-aligned cells. Turn it into one sub-row per line."""
    label_j = next((j for j, c in enumerate(row) if len(c.lines) >= 3 and c.valign != "bottom"), None)
    if label_j is None:
        return None
    L = len(row[label_j].lines)
    multi = [c for c in row if c.valign == "bottom" and c.lines]
    if not multi or any(len(c.lines) >= L for c in multi):
        return None
    subs = []
    head = row[label_j].lines[0]
    for i in range(1, L):
        vals = []
        for j, c in enumerate(row):
            if j == label_j:
                vals.append(f"{head} {row[label_j].lines[i].lstrip('- ')}")
            elif c.valign == "bottom":
                pad = [""] * (L - len(c.lines)) + c.lines
                vals.append(pad[i])
            else:
                vals.append(c.text if i == 1 else "")
        subs.append(vals)
    return subs


LONG_CELL = 20   # words; a vertically merged cell longer than this is not repeated per row


def _collapse_long_vmerge(rows: list) -> list:
    """Rows sharing one long vertically merged cell (e.g. one scholarship policy for 6 majors)
    become ONE row whose other cells list all values: the policy text is written once instead
    of 6 times. Short merged cells ("Đạt (Tích lũy)") are still repeated - they are context."""
    out: list = []
    for row in rows:
        if out:
            prev = out[-1]
            shared = [j for j, c in enumerate(row) if j < len(prev) and c.key == prev[j].key
                      and n_words(c.text) > LONG_CELL]
            if shared:
                merged = []
                for j, c in enumerate(row):
                    p = prev[j]
                    if c.key == p.key or not c.text or c.text in p.text.split(", "):
                        merged.append(p)
                    else:
                        merged.append(type(c)(f"{p.text}, {c.text}" if p.text else c.text, p.key, p.bold,
                                              p.lines + c.lines, p.valign))
                out[-1] = merged
                continue
        out.append(list(row))
    return out


def _row_pieces(prefix: str, fields: list[str], max_words: int) -> list[str]:
    """One table row -> one line, or several lines when it is longer than max_words: the longest
    field is cut between its sub-lines (or sentences) and every piece repeats the other fields,
    so 'Ngành học: ...' is never separated from the policy text that applies to it."""
    line = prefix + " | ".join(fields)
    if n_words(line) <= max_words:
        return [line]
    i = max(range(len(fields)), key=lambda k: n_words(fields[k]))
    name, _, value = fields[i].partition(": ")
    if not value:
        name, value = "", fields[i]
    others = prefix + " | ".join(f for k, f in enumerate(fields) if k != i)
    budget = max(60, max_words - n_words(others) - 8)
    parts = [x for x in value.split("; ") if x]
    if len(parts) == 1:
        parts = RE_SENT.split(value)
    groups, buf = [], []
    for x in parts:
        if buf and n_words("; ".join(buf + [x])) > budget:
            groups.append(buf)
            buf = []
        buf.append(x)
    groups.append(buf)
    n = len(groups)
    return [f"{others} | {name} (phần {k}/{n}): {'; '.join(g)}" if name else f"{others} | (phần {k}/{n}) {'; '.join(g)}"
            for k, g in enumerate(groups, 1)]


def table_units(t: Table, caption: str, legend: dict[str, str], max_words: int = 300) -> list[Unit]:
    names, groups = _header_names(t, legend)
    skip = {j for j, nm in enumerate(names) if nm.strip(" .").lower() in SKIP_COLS}
    units: list[Unit] = []
    label = ""
    for row in _collapse_long_vmerge(t.rows[t.n_header:]):
        keys = [c.key for j, c in enumerate(row) if j not in skip]
        cells = [c for j, c in enumerate(row) if j not in skip]
        # spanning row (one merged cell over (almost) all columns) that reads like a sub-title
        # -> becomes a label prefixed to the following rows, and is also kept as a line.
        span = max((keys.count(k) for k in set(keys)), default=0)
        if cells and span >= len(cells) - 1 and len(cells) > 1:
            big = max(cells, key=lambda c: keys.count(c.key))
            others = {c.text for c in cells if c.key != big.key and c.text}
            if big.text and (is_caps(big.text) or big.bold > 0.85 or big.text.endswith(":")):
                lab = " – ".join([*sorted(others), big.text]) if others else big.text
                label = lab.rstrip(":")
                units.append(Unit(lab, kind="row", table=caption))
                continue
        rows_vals = _expand_aligned(row) or [[c.text for c in row]]
        for vals in rows_vals:
            fields, seen, last_group = [], set(), None
            for j, v in enumerate(vals):
                if j in skip or j >= len(names):
                    continue
                k = row[j].key
                if k in seen or not v:
                    continue
                seen.add(k)
                span_cols = [x for x in range(len(row)) if row[x].key == k and x not in skip]
                first_nm, last_nm = names[span_cols[0]], names[span_cols[-1]]
                nm = first_nm if first_nm == last_nm else f"{first_nm} → {last_nm}"
                if fields and nm and fields[-1].startswith(f"{nm}: "):   # two cells under one header
                    fields[-1] += f" – {_join_lines(v)}"
                    last_group = None
                    continue
                v = _join_lines(v)
                if label and v in label:          # already said by the row label
                    continue
                g = groups[j] if len(span_cols) == 1 else None
                item = f"{nm}: {v}" if nm else v
                if g and g == last_group:
                    fields[-1] += f", {item}"          # "Thang điểm hệ 4 – Điểm chữ: A+, Điểm số: 4"
                else:
                    fields.append(f"{g} – {item}" if g else item)
                last_group = g
            num = next((vals[j].strip() for j in skip if j < len(vals) and re.fullmatch(r"\d+\.?", vals[j].strip())), "")
            if fields:
                prefix = (f"[{label}] " if label else "") + (f"{num.rstrip('.')}. " if num else "")
                for piece in _row_pieces(prefix, fields, max_words):
                    units.append(Unit(piece, kind="row", table=caption))
    return units


# --------------------------------------------------------------------------- sections
def join_heading(prev: str, nxt: str) -> str:
    """'Chương I' + 'QUY ĐỊNH CHUNG' -> 'Chương I. QUY ĐỊNH CHUNG'; other titles just continue."""
    if RE_CHAPTER.fullmatch(prev.strip()) or re.fullmatch(r"(chương|phụ lục)\s+[ivxlc\d]+\.?", prev.strip(), re.I):
        return f"{prev.strip().rstrip('.')}. {nxt}"
    return f"{prev.rstrip()} {nxt}"


def classify(doc: DocBlocks) -> list[tuple[str, object, int | None]]:
    """-> [("head", text, rank) | ("para", Para, None) | ("table", Table, None)] without title lines."""
    out: list = []
    started = False
    blocks = doc.blocks
    for i_b, b in enumerate(blocks):
        next_is_table = i_b + 1 < len(blocks) and isinstance(blocks[i_b + 1], Table)
        if isinstance(b, Table):
            out.append(("table", b, None))
            started = True
            continue
        r = heading_rank(b)
        unnumbered_title = b.centered and b.bold > 0.85 and r != RANK_ARTICLE and not (
            RE_CHAPTER.match(b.text) or RE_ROMAN.match(b.text) or RE_NUM.match(b.text))
        if not started and unnumbered_title:
            continue                        # document title lines, e.g. "QUY CHẾ" / "TRÌNH ĐỘ ĐẠI HỌC"
        started = True
        # a centred bold line right after a heading continues it ("Chương I" + "QUY ĐỊNH CHUNG")
        if (out and out[-1][0] == "head" and b.centered and b.bold > 0.85
                and not (RE_CAPTION.match(b.text) and next_is_table) and (r is None or r in (RANK_CHAPTER, RANK_LABEL))
                and not (RE_CHAPTER.match(b.text) or RE_ROMAN.match(b.text))):
            out[-1] = ("head", join_heading(out[-1][1], b.text), out[-1][2])
            continue
        if r is not None:
            out.append(("head", b.text, r))
        else:
            out.append(("para", b, None))
    # "1. Sinh viên được nhận thư khen thỏa các điều kiện:" followed by sub-titles is a heading
    # in disguise (not bold): promote it so the sub-titles hang under it.
    for i, (k, obj, _r) in enumerate(out[:-1]):
        if k == "para" and RE_NUM.match(obj.text) and obj.text.rstrip().endswith(":") \
                and n_words(obj.text) <= 30 and out[i + 1][0] == "head" and out[i + 1][2] > RANK_NUM:
            out[i] = ("head", obj.text, RANK_NUM)
    return out


def sectionize(doc: DocBlocks, max_words: int = 300) -> list[Section]:
    items = classify(doc)
    has_articles = any(k == "head" and r == RANK_ARTICLE for k, _, r in items)
    has_numbered = any(k == "head" and r <= RANK_NUM for k, _, r in items)
    # Articles are THE unit of a legal text. Guides without articles are cut at their "1." level
    # (one scholarship type, one office...); deeper sub-titles (1.1, 1.2, "Lưu ý:") stay inside.
    cut_rank = RANK_ARTICLE if has_articles else (RANK_NUM if has_numbered else RANK_LABEL)
    stack: list[tuple[int, str]] = []
    sections = [Section(path=[])]
    pending_caption, pending_legend = "", {}
    last_num = 0          # number of the last "N." heading, to detect "N+1." written as plain text
    for idx, (kind, obj, rank) in enumerate(items):
        cur = sections[-1]
        if kind == "head" and rank == RANK_NUM:
            last_num = int(obj.split(".")[0]) if obj.split(".")[0].isdigit() else last_num
        if (kind == "para" and not has_articles and stack and stack[-1][0] >= RANK_NUM and last_num
                and RE_NUM.match(obj.text) and int(obj.text.split(".")[0]) == last_num + 1):
            # "2. ..." after the sub-titles of "1." belongs to the parent level, not to the last
            # sub-title: close the sub-sections and continue at the parent's level.
            while stack and stack[-1][0] >= RANK_NUM:
                stack.pop()
            last_num += 1
            sections.append(Section(path=[h for _, h in stack]))
            cur = sections[-1]
        if kind == "head" and rank <= cut_rank:
            while stack and stack[-1][0] >= rank:
                stack.pop()
            stack.append((rank, obj))
            m = RE_ARTICLE.match(obj)
            sections.append(Section(path=[h for _, h in stack], article=int(m.group(1)) if m else
                                    (cur.article if rank > RANK_ARTICLE and has_articles else None)))
            continue
        if kind == "head":                       # deeper heading inside an article: keep inline
            cur.units.append(Unit(obj, kind="heading", khoan=_khoan(obj) if has_articles else None, sub=obj))
            continue
        sub = next((u.sub for u in reversed(cur.units) if u.sub), None)
        if kind == "para":
            t = obj.text
            nxt = items[idx + 1][0] if idx + 1 < len(items) else None
            if RE_CAPTION.match(t.strip("*")) and nxt == "table" or (obj.italic > 0.8 and obj.centered and nxt == "table"):
                pending_caption = t
                continue
            leg = parse_legend(t)
            if leg and nxt == "table":
                pending_legend = leg
            cur.units.append(Unit(t, kind="para", khoan=_khoan(t) if has_articles else None, sub=sub))
            continue
        # table
        caption = pending_caption or (cur.path[-1] if cur.path else doc.title)
        # the sentence that introduces the table ("6.2. Điều kiện ...:") becomes its caption, so it
        # is repeated on every chunk the table is split into instead of being left behind
        lead = None
        if not pending_caption and cur.units and cur.units[-1].kind in ("para", "heading") \
                and cur.units[-1].text.rstrip().endswith(":") and n_words(cur.units[-1].text) <= 40:
            lead = cur.units.pop()
            caption = lead.text.rstrip().rstrip(":")
        rows = table_units(obj, caption, pending_legend, max_words)
        for r_ in rows:
            r_.sub = sub
        if rows:
            rows[0].first = True
            if lead is not None:
                rows[0].khoan = lead.khoan
        cur.units.extend(rows)
        pending_caption, pending_legend = "", {}
    return [s for s in sections if s.units and not (s.path and s.path[-1].strip(": ").lower() == "nguồn")]


def _khoan(text: str) -> str | None:
    m = RE_KHOAN.match(text)
    return text.split(".")[0] if m else None


def merge_small(sections: list[Section], min_words: int, max_words: int) -> list[Section]:
    """Glue sections shorter than min_words to the previous section when it is their parent or
    sibling (same document part) and the result still fits; otherwise to the next one."""
    out: list[Section] = []
    for s in sections:
        if out:
            p = out[-1]
            related = s.path[: len(p.path)] == p.path or s.path[:-1] == p.path[:-1]
            same_article = s.article == p.article
            limit = int(max_words * TABLE_SLACK)
            if s.words < min_words and related and same_article and p.words + s.words <= limit:
                child = s.path[: len(p.path)] == p.path
                extra = s.path[len(p.path):] if child else s.path[-1:]
                p.units.extend([Unit(h, kind="heading") for h in extra] + s.units)
                if not child and p.path and s.path:            # siblings: "9. Thư viện; 10. Viện ..."
                    p.path = p.path[:-1] + [f"{p.path[-1].rstrip(':')}; {s.path[-1]}"]
                continue
            if p.words < min_words and (s.path[: len(p.path)] == p.path or s.path[:-1] == p.path[:-1]) \
                    and same_article and p.words + s.words <= limit:
                head = p.path[len(s.path) - 1:] if s.path[:-1] == p.path[:-1] and p.path else []
                s.units = [Unit(h, kind="heading") for h in head] + p.units + s.units
                s.path = s.path if s.path[: len(p.path)] == p.path else s.path[:-1] or s.path
                out[-1] = s
                continue
        out.append(s)
    return out


# --------------------------------------------------------------------------- splitting
def _group_units(units: list[Unit], article_doc: bool, max_words: int) -> list[Unit]:
    """Attach points a), b), - ... to the khoản (or heading) they belong to, so packing never
    separates "1. Điều kiện:" from its list. A table that fits in one chunk becomes ONE unit,
    glued to the sentence that introduces it ("... theo Bảng 1:"); a bigger table stays one
    unit per row so it can be split between rows (never inside a row)."""
    units = _merge_small_tables(units, max_words)
    out: list[Unit] = []
    for u in units:
        starts_new = (u.kind != "para" or not out or out[-1].kind in ("row", "table")
                      or (article_doc and u.khoan is not None)
                      or (not article_doc and not RE_POINT.match(u.text)))
        if starts_new:
            out.append(replace(u, kind=u.kind if u.kind != "heading" else "para"))
        elif out[-1].kind == "table":
            out.append(replace(u, kind="para"))
        else:
            out[-1].text += "\n" + u.text
    return out


TABLE_SLACK = 1.3   # a table may exceed max_words by 30% rather than be cut in two


def _merge_small_tables(units: list[Unit], max_words: int) -> list[Unit]:
    limit = int(max_words * TABLE_SLACK)
    out: list[Unit] = []
    i = 0
    while i < len(units):
        u = units[i]
        if u.kind != "row":
            out.append(u)
            i += 1
            continue
        j = i
        while j < len(units) and units[j].kind == "row" and units[j].table == u.table:
            j += 1
        rows = units[i:j]
        if not rows[0].first:          # a table already cut by the section split: keep rows
            out.extend(rows)
            i = j
            continue
        body = "\n".join(r.text for r in rows)
        if n_words(body) <= limit:
            table = Unit(f"Bảng: {u.table}\n{body}", kind="table", khoan=None, table=u.table)
            prev = out[-1] if out else None
            if prev is not None and prev.kind in ("para", "heading") and n_words(prev.text) + table.words <= limit:
                out[-1] = Unit(f"{prev.text}\n{table.text}", "table", prev.khoan, u.table)
            else:
                out.append(table)
        else:
            out.extend(rows)
        i = j
    return out


RE_ENUM = re.compile(r"(?<=[;.])\s+(?=\(\d+\)\s)")


def _pieces(text: str, max_words: int) -> list[str]:
    """Lines; a line still too long is cut at sentences, then at '(1) ... ; (2) ...'."""
    out = []
    for line in text.split("\n"):
        if n_words(line) <= max_words:
            out.append(line)
            continue
        for sent in RE_SENT.split(line):
            out.extend(RE_ENUM.split(sent) if n_words(sent) > max_words else [sent])
    return out


def _split_long(u: Unit, max_words: int) -> list[Unit]:
    """A single unit longer than max_words: cut at line breaks, then sentences, then '(n)' items."""
    if u.words <= max_words:
        return [u]
    pieces = _pieces(u.text, max_words)
    head = ""
    if u.kind == "row" and u.text.startswith("["):
        head = pieces[0] + "\n"          # keep the row label on every piece
        pieces = pieces[1:]
    total = n_words(u.text)
    target = total / -(-total // max_words)            # equal parts instead of "full + crumbs"
    out, buf = [], []
    for p in pieces:
        if buf and (n_words("\n".join(buf + [p])) > max_words or n_words("\n".join(buf)) >= target):
            out.append(replace(u, text=head + "\n".join(buf), first=u.first and not out))
            buf = []
        buf.append(p)
    if buf:
        out.append(replace(u, text=head + "\n".join(buf), first=u.first and not out))
    return out


def pack(units: list[Unit], max_words: int, min_tail: int) -> list[list[Unit]]:
    """Greedy packing towards EQUAL sizes: with 330 words and max 300 we want 165+165, not 300+30."""
    total = sum(u.words for u in units)
    if total <= max_words:
        return [units]
    target = total / max(1, -(-total // max_words))
    packs: list[list[Unit]] = [[]]
    for u in units:
        cur = packs[-1]
        size = sum(x.words for x in cur)
        if cur and (size + u.words > max_words or size >= target * 0.9):
            packs.append([])
        packs[-1].append(u)
    # a very short last pack is folded back if that stays reasonable
    if len(packs) > 1 and sum(x.words for x in packs[-1]) < min_tail and \
            sum(x.words for x in packs[-2] + packs[-1]) <= int(max_words * 1.25):
        packs[-2].extend(packs.pop())
    return packs


# --------------------------------------------------------------------------- main entry
def chunk_document(doc: DocBlocks, max_words: int = 300, min_words: int = 50,
                   meta: dict | None = None) -> list[Chunk]:
    meta = meta or {}
    sections = merge_small(sectionize(doc, max_words), min_words, max_words)
    article_doc = any(s.article is not None for s in sections)
    chunks: list[Chunk] = []
    for s in sections:
        units = []
        for u in _group_units(s.units, article_doc, max_words):
            units.extend(_split_long(u, int(max_words * TABLE_SLACK) if u.kind == "table" else max_words))
        packs = pack(units, max_words, min_tail=min_words)
        for k, p in enumerate(packs, 1):
            lines, cur_table = [], None
            for u in p:
                if u.kind == "row" and u.table != cur_table:
                    cont = "" if u.first else " (tiếp theo)"
                    lines.append(f"Bảng: {u.table}{cont}")
                    cur_table = u.table
                elif u.kind != "row":
                    cur_table = None
                lines.append(u.text)
            ctx = f"Văn bản: {doc.title}"
            if s.path:
                ctx += "\nMục: " + " > ".join(s.path)
            head = p[0]
            if head.sub and not head.text.startswith(head.sub):   # chunk starts inside a sub-title
                ctx += ("\nMục: " if not s.path else " > ") + f"{head.sub.rstrip(':')} (tiếp)"
            if len(packs) > 1:
                ctx += f" (phần {k}/{len(packs)})"
            chunks.append(Chunk(
                id=f"{doc.doc_id}#{len(chunks) + 1:03d}", doc_id=doc.doc_id, doc_title=doc.title,
                path=s.path, text="\n".join(lines),
                context=ctx, article=s.article,
                khoan=sorted({u.khoan for u in p if u.khoan}, key=lambda x: int(x)),
                part=(k, len(packs)), has_table=any(u.kind in ("row", "table") for u in p), meta=dict(meta),
            ))
    return chunks


def chunk_corpus(docs: list[DocBlocks], manifest: list[dict] | None = None, **kw) -> list[Chunk]:
    info = {m["id"]: m for m in (manifest or [])}
    out = []
    for d in docs:
        m = info.get(d.doc_id, {})
        out.extend(chunk_document(d, meta={"in_force": m.get("in_force", True), "origin": m.get("origin", "internal")}, **kw))
    return out
