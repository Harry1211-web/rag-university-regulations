from src.rag.chunk import chunk_document, heading_rank, parse_legend
from src.rag.ingest import Para

LONG = " ".join(["từ"] * 120)


def test_heading_rank():
    assert heading_rank(Para("Điều 12. Khối lượng học tập", bold=0.0)) == 3   # article, any style
    assert heading_rank(Para("Chương II", bold=1.0, centered=True)) == 1
    assert heading_rank(Para("1. Học bổng thủ khoa", bold=1.0)) == 4
    assert heading_rank(Para("1.2. Điều kiện:", bold=1.0)) == 5
    assert heading_rank(Para("Thông tin liên hệ:", bold=1.0)) == 7
    assert heading_rank(Para("1. Sinh viên phải đăng ký môn học.", bold=0.0)) is None   # body text


def test_article_document_one_chunk_per_article(builder, tmp_path):
    doc = (builder.title("QUY CHẾ").title("ĐÀO TẠO")
           .head("Chương I", centered=True).head("QUY ĐỊNH CHUNG", centered=True)
           .head("Điều 1. Phạm vi").para("1. Quy chế này áp dụng cho sinh viên.").para("2. Không áp dụng cho học viên.")
           .head("Điều 2. Tín chỉ").para("1. Một tín chỉ bằng 50 giờ học tập.")
           .build(tmp_path))
    chunks = chunk_document(doc, min_words=5)
    assert [c.article for c in chunks] == [1, 2]
    # title lines are dropped, "Chương I" + its name are joined, the context carries the path
    assert chunks[0].path == ["Chương I. QUY ĐỊNH CHUNG", "Điều 1. Phạm vi"]
    assert "Mục: Chương I. QUY ĐỊNH CHUNG > Điều 1. Phạm vi" in chunks[0].context
    assert "QUY CHẾ" not in chunks[0].text
    assert chunks[0].khoan == ["1", "2"]


def test_long_article_is_split_between_khoan_never_inside(builder, tmp_path):
    b = builder.head("Điều 5. Thời gian")
    for k in range(1, 6):
        b.para(f"{k}. Khoản {k} {LONG}")
        b.para(f"a) điểm a của khoản {k}")
    chunks = chunk_document(b.build(tmp_path), max_words=300, min_words=10)
    assert len(chunks) > 1 and all(c.article == 5 for c in chunks)
    for c in chunks:
        # every "a)" stays in the same chunk as the khoản it belongs to
        for k in c.khoan:
            assert f"a) điểm a của khoản {k}" in c.text
        assert c.n_words <= 300
    assert chunks[0].part == (1, len(chunks))
    assert "(phần 1/" in chunks[0].context


def test_small_sections_are_merged_with_their_sibling(builder, tmp_path):
    doc = (builder.head("1. Phòng Đại học").para(LONG)
           .head("2. Thư viện").para("Tòa nhà G.")
           .build(tmp_path))
    chunks = chunk_document(doc, min_words=50)
    assert len(chunks) == 1
    assert chunks[0].path == ["1. Phòng Đại học; 2. Thư viện"]
    assert "2. Thư viện" in chunks[0].text and "Tòa nhà G." in chunks[0].text


def test_guide_cut_at_numbered_level_subtitles_stay_inside(builder, tmp_path):
    doc = (builder.head("I. HỌC BỔNG TÂN SINH VIÊN")
           .head("1. Học bổng Thủ khoa").para("Đối tượng: sinh viên thủ khoa. " + LONG)
           .head("1.2. Điều kiện và mức xét cấp học bổng:").para("Cấp 100% học phí.")
           .head("2. Học bổng tỉnh ký kết").para(LONG)
           .build(tmp_path))
    chunks = chunk_document(doc, min_words=10)
    assert [c.path[-1] for c in chunks] == ["1. Học bổng Thủ khoa", "2. Học bổng tỉnh ký kết"]
    assert "Cấp 100% học phí." in chunks[0].text


def test_small_table_stays_whole_with_its_lead_in(builder, tmp_path):
    doc = (builder.head("Điều 24. Thang điểm")
           .para("1. Thang điểm được quy định theo Bảng 1:")
           .para("Bảng 1. Thang điểm đánh giá")
           .table([["Xếp loại", "Điểm"], ["Giỏi", "8,0"], ["Khá", "7,0"]])
           .build(tmp_path))
    (c,) = chunk_document(doc, min_words=5)
    assert c.has_table
    assert "Bảng: Bảng 1. Thang điểm đánh giá\nXếp loại: Giỏi | Điểm: 8,0\nXếp loại: Khá | Điểm: 7,0" in c.text
    assert c.text.index("theo Bảng 1:") < c.text.index("Xếp loại: Giỏi")


def test_legend_codes_are_expanded_and_aligned_rows_split(builder, tmp_path):
    doc = (builder.para("Hình thức xử lý: (1): Nhắc nhở - (2): Phê bình - (3): Khiển trách")
           .table([["Nội dung", "Số lần", None, None], [None, "(1)", "(2)", "(3)"],
                   ["Vi phạm quy chế thi:\n- Đình chỉ thi\n- Trừ 25%", "", "Lần 1", "Lần 1\nLần 2"]],
                  header_rows=2, merges=[((0, 1), (0, 3)), ((0, 0), (1, 0))], bottom=[(2, 2), (2, 3)])
           .build(tmp_path))
    text = "\n".join(c.text for c in chunk_document(doc, min_words=1))
    assert "(2) Phê bình" in text
    # one sub-row per line of the first cell, codes aligned from the bottom
    assert "Vi phạm quy chế thi: Đình chỉ thi | Số lần – (3) Khiển trách: Lần 1" in text
    assert "Vi phạm quy chế thi: Trừ 25% | Số lần – (2) Phê bình: Lần 1, (3) Khiển trách: Lần 2" in text


def test_long_vertically_merged_cell_written_once(builder, tmp_path):
    policy = "Học bổng 50% học phí cho thí sinh khu vực 1. " + " ".join(["chi tiết"] * 15)
    doc = (builder.head("6. Ngành thu hút")
           .table([["Ngành học", "Chính sách"], ["Công tác xã hội", policy], ["Bảo hộ lao động", None]],
                  merges=[((1, 1), (2, 1))])
           .build(tmp_path))
    (c,) = chunk_document(doc, min_words=1)
    assert c.text.count("Học bổng 50%") == 1
    assert "Ngành học: Công tác xã hội, Bảo hộ lao động" in c.text


def test_parse_legend():
    assert parse_legend("(1): Nhắc nhở - (2): Phê bình - (3): Nghiêm khắc phê bình.") == {
        "(1)": "Nhắc nhở", "(2)": "Phê bình", "(3)": "Nghiêm khắc phê bình"}
    assert parse_legend("không có chú giải") == {}


def test_chunk_dict_has_metadata(builder, tmp_path):
    doc = builder.head("Điều 1. A").para("1. Nội dung.").build(tmp_path)
    d = chunk_document(doc, min_words=1, meta={"in_force": True, "origin": "internal"})[0].to_dict()
    for k in ("id", "doc_id", "loc", "article", "khoan", "context", "text", "sha1", "in_force", "origin"):
        assert k in d
    assert d["id"] == "test#001" and d["loc"] == "Điều 1"
