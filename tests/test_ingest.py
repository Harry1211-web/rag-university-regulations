import unicodedata

from src.rag.ingest import Para, Table, normalize


def test_normalize_nfc_and_spaces():
    nfd = unicodedata.normalize("NFD", "Điều  kiện\u00a0tốt   nghiệp")
    assert normalize(nfd) == "Điều kiện tốt nghiệp"
    assert unicodedata.is_normalized("NFC", normalize(nfd))


def test_blocks_keep_order_and_formatting(builder, tmp_path):
    doc = (builder.title("QUY CHẾ").head("Điều 1. Phạm vi").para("1. Nội dung.")
           .table([["A", "B"], ["1", "2"]]).para("Sau bảng.").build(tmp_path))
    kinds = [type(b).__name__ for b in doc.blocks]
    assert kinds == ["Para", "Para", "Para", "Table", "Para"]
    t: Para = doc.blocks[0]
    assert t.centered and t.bold == 1.0
    assert doc.blocks[2].bold == 0.0


def test_table_merged_cells_share_a_key(builder, tmp_path):
    doc = builder.table(
        [["Nhóm", "Ngành", "Mức"], ["Nhóm 1", "Công tác xã hội", "20%"], [None, "Bảo hộ lao động", "20%"]],
        merges=[((1, 0), (2, 0))],
    ).build(tmp_path)
    t: Table = doc.blocks[0]
    assert t.n_header == 1
    # vertical merge: the continuation row sees the same cell
    assert t.rows[2][0].text == "Nhóm 1" and t.rows[2][0].key == t.rows[1][0].key


def test_bottom_aligned_cell_keeps_lines(builder, tmp_path):
    doc = builder.table([["Nội dung", "(1)"], ["Mức:\n- A\n- B", "Lần 1"]], bottom=[(1, 1)]).build(tmp_path)
    cell = doc.blocks[0].rows[1][1]
    assert cell.valign == "bottom" and cell.lines == ["Lần 1"]
