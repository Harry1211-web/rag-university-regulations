# Chunking design

Code: [`src/rag/ingest.py`](../src/rag/ingest.py) (docx → blocks) and [`src/rag/chunk.py`](../src/rag/chunk.py) (blocks → chunks).
Output of a run: [`reports/chunk_stats.md`](../reports/chunk_stats.md).

## Goals

1. **A chunk is a unit a student would cite.** For a regulation that is an *Điều* (article), or one or more
   *khoản* (clauses) of a long article. For a guide it is a numbered item ("6. Học bổng ngành thu hút").
2. **Never cut inside the smallest legal unit.** A clause stays together with its points `a) b) c)`
   and its `-` bullets. A table row is never split mid-row unless one row alone is over the size limit.
3. **Every chunk can be read on its own.** A context header (document title + section path) is
   embedded with the text. A table row repeats its column names.
4. **The size fits a small multilingual embedder.**

## Pipeline

```
docx ──ingest──► blocks (Para / Table, in body order, NFC)
     ──classify──► heading / paragraph / table   (+ drop title lines, join "Chương II" + its name)
     ──sectionize──► sections = (path, units)    (cut at Chương / Điều / numbered heading)
     ──merge_small──► glue sections < min_words to a sibling or parent
     ──group + split + pack──► chunks ≤ max_words, cut between clauses / rows only
     ──render──► context header + text + metadata
```

### 1. Ingest
- python-docx is iterated over the body XML, so paragraphs and tables come out in the right order.
- Text is normalized to **NFC** with whitespace collapsed. Vietnamese has two encodings for the same
  letter (precomposed vs combining marks). Without this, "Điều" would not match "Điều".
- Each paragraph keeps its formatting: bold ratio, italic ratio, centered. These signals are what
  separate headings from body text.
- For tables, each cell keeps:
  - its paragraphs (lines);
  - its bold ratio;
  - a *merge key*, so vertically or horizontally merged cells are recognized as one cell;
  - its vertical alignment.

  The header rows are the leading rows marked "repeat as header row" (`w:tblHeader`).

### 2. Classify: heading ranks
| Rank | Pattern | Example |
|---|---|---|
| 1 | `Chương N` | Chương III |
| 2 | Roman numeral | I. HỌC BỔNG TÂN SINH VIÊN |
| 3 | `Điều N.` (any style) | Điều 24. Thang điểm đánh giá |
| 4 | `N.` bold, short | 6. Học bổng ngành thu hút |
| 5 | `N.N.` bold | 6.2. Điều kiện và mức xét |
| 6 | `N.N.N.` bold | 1.2.1. … |
| 7 | short bold line, no number | Thông tin liên hệ: |

A numbered line that is **not bold** is body text (`1. Sinh viên phải …` is a khoản, not a heading).
Rank 3 is the exception: an `Điều` is recognized from its text alone.

The title block (all-caps centered lines before the first heading) is dropped. It is already carried
by `doc_title`, and repeating "QUY CHẾ ĐÀO TẠO" in every chunk only adds noise.

### 3. Sectionize: where to cut
- **Documents with articles** (they contain `Điều N.`) are cut at Chương and Điều. Everything below
  stays inside the article and is handled by the packer.
- **Guides and announcements** (no articles) are cut at rank ≤ 4, i.e. at the `1.` level. Ranks 5–7
  are kept as heading lines *inside* the chunk.
  - Example: "1.2. Điều kiện và mức xét cấp học bổng" belongs with "1. Học bổng Thủ khoa". The
    conditions only make sense next to the scholarship they belong to.
  - When such a chunk must still be split, the sub-title is added to the context of the
    continuation: `… > 6.2. Điều kiện và mức xét cấp học bổng (tiếp)`.

### 4. Merge small sections
A section under `min_words` (50) is glued to the previous section when that section is its parent or
sibling and the result is ≤ `max_words × 1.3`. Otherwise it is glued forward to the next one.
- Sibling titles are joined: `9. Thư viện; 10. Viện …`, so the merged title stays searchable.
- Articles are never merged with each other. One Điều is one citable unit, even if it is short.

### 5. Group, split, pack
- **Group**:
  - in an article document, a unit starts at every clause `N.`;
  - in a guide, a unit starts at every line that is not a point (`a)`, `-`, `+`, `▪`);
  - points and bullets are appended to the unit above them.
- **Tables**:
  - A table that fits (≤ `max_words × 1.3`) becomes **one** unit, glued to the sentence that
    introduces it ("… được quy định theo Bảng 1:").
  - A larger table is one unit per row.
- **Split**: a single unit over `max_words` is cut at line breaks, then at sentences, then at
  enumerations `(1) … ; (2) …`. It is cut into *equal* parts.
- **Pack**: units are packed greedily towards equal sizes. For example, 330 words gives 165 + 165,
  not 300 + 30. A tail under `min_words` is folded back into the previous pack when that stays
  ≤ `max_words × 1.25`. A section that fits is never split.

### 6. Render
```
Văn bản: Quy chế tổ chức và quản lý đào tạo trình độ đại học
Mục: Chương III. ĐÁNH GIÁ KẾT QUẢ HỌC TẬP > Điều 24. Thang điểm đánh giá (phần 1/2)

1. Điểm đánh giá thành phần … được quy định theo Bảng 1:
Bảng: Bảng 1. Thang điểm đánh giá
Đạt (Tích lũy) | Xếp loại: Giỏi | Thang điểm hệ 10: từ 8,0 đến cận 9,0 | Thang điểm hệ 4 (tham khảo) – Điểm chữ: A, Điểm số: 3.5
…
```
The embedded string is `context + "\n\n" + text`. The metadata carries `doc_id`, `path`, `loc`
(e.g. `Điều 24 khoản 1`), `article`, `khoan`, `part`, `has_table`, `in_force`, `origin` and the
`sha1` of the text.

## Tables

Each table row becomes one line of `Column: value | Column: value`. Rows that span all columns
become labels. The rules below handle the real tables in the corpus.

| Problem | Rule |
|---|---|
| Two header rows ("Thang điểm hệ 4" over "Điểm chữ / Điểm số") | Names are joined: `Thang điểm hệ 4 (tham khảo) – Điểm chữ: A+, Điểm số: 4` |
| Codes in the header, legend in a paragraph above ("(1): Nhắc nhở - (2): Phê bình …") | The legend is parsed and the codes are expanded: `(2) Phê bình: Lần 1` |
| Row spanning the table ("Đạt (Tích lũy)", a group title) | Becomes a label prefixed to the following rows |
| `TT` / `STT` columns | Dropped; a numeric value is kept as the row prefix `28.` |
| One cell with several lines facing cells aligned to the bottom (Phụ lục vi phạm, row 28) | The row is expanded to one sub-row per line, and the bottom-aligned cells are padded from the bottom so "Lần 1" faces the right line |
| A long cell vertically merged over many rows (a scholarship policy shared by 6 majors) | Written once; the short cells of the merged rows are joined: `Ngành học: A, B, C` |
| A row over the size limit | Split into pieces that each repeat the other (short) fields, marked `(phần 1/2)` |
| A table split across chunks | Each continuation chunk repeats the caption with `(tiếp theo)` |

## Size limits

| Setting | Value | Why |
|---|---|---|
| `max_words` | 300 | See below |
| `min_words` | 50 | Below this a chunk is too thin for retrieval and is merged |
| `TABLE_SLACK` | 1.3 | A table or a small merge may go up to 390 words rather than be cut |

"Words" are whitespace tokens. In Vietnamese that means syllables. The current corpus has 337 chunks:
- median 216 words;
- p90 289;
- max 376 (a table kept whole);
- min 22 (a short Điều that must stay its own chunk).

**Assumption, not yet measured:** 300 syllables plus a ~30-word header stays under 512 subword
tokens for the multilingual embedders we plan to compare (e.g. multilingual-e5). This could not be
checked in the build environment, where the tokenizer download was blocked. The indexing notebook
measures it with the real tokenizer and reports any chunk that would be truncated.

## Verification

- `scripts/build_chunks.py` maps every citation in `eval/golden.jsonl` to chunk ids (`eval/gold_chunks.json`).
  - It narrows down to khoản and điểm level, or to the exact chunk when the citation carries a verbatim quote.
  - All 143 answerable questions resolve.
  - This mapping is the ground truth for Recall@k in the retrieval ablation.
- `tests/` builds small .docx files in code (no corpus needed). They check:
  - NFC normalization;
  - merged cells, `tblHeader` and `vAlign`;
  - one chunk per article;
  - splits only between clauses;
  - sibling merge;
  - guide-level cutting;
  - table + lead-in;
  - legend expansion and bottom alignment;
  - the merged long cell written once;
  - the citation resolver.

## Known limitations

- `max_words` is soft: a table kept whole can reach 1.3× (376 words).
- A few articles are shorter than `min_words` (e.g. 22–25 words). They are kept as is because one Điều
  is one citable unit.
- Numbered paragraphs that follow the last heading of a guide have no section path, e.g.
  dk-thu-khen items 2–3. Their `loc` is "(không có mục)".
- There are no page numbers. The docx files were rebuilt from scans, so citations point to
  Điều/khoản/mục, not pages.
- Heading detection relies on bold and centering. A new document with inconsistent formatting
  may need a rule.
