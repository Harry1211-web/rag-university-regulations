from src.rag.chunk import Chunk
from src.rag.llm import REFUSAL, FakeLLM
from src.rag.report import chunk_stats, golden_coverage

MANIFEST = [{"id": "qc", "file": "QUY CHẾ.docx"}, {"id": "pb", "file": "PHÒNG BAN.docx"}]


def _c(i, doc, path, text, article=None, khoan=(), part=(1, 1)):
    return Chunk(id=f"{doc}#{i:03d}", doc_id=doc, doc_title=doc, path=path, text=text, context="",
                 article=article, khoan=list(khoan), part=part)


CHUNKS = [
    _c(1, "qc", ["Điều 25"], "1. Điểm F ...", 25, ["1"], (1, 2)),
    _c(2, "qc", ["Điều 25"], "2. Điểm H ...\na) điều kiện\nb) Thủ tục ...", 25, ["2"], (2, 2)),
    _c(3, "pb", ["4. Phòng đại học:"], "Phòng A0005"),
    _c(4, "pb", ["5. Văn phòng tư vấn"], "5.1 Tư vấn học vụ\n5.2 Tâm lý học đường"),
]


def test_resolve_article_khoan_and_sections():
    rows = [
        {"id": "q1", "citations": [{"doc": "QUY CHẾ", "loc": "Điều 25 khoản 2 điểm b"}]},
        {"id": "q2", "citations": [{"doc_id": "qc", "loc": "Điều 25 khoản 1"}]},
        {"id": "q3", "citations": [{"doc": "PHÒNG BAN", "loc": "mục 5.2"}]},
        {"id": "q4", "citations": []},                       # "not in the documents" question
        {"id": "q5", "citations": [{"doc": "KHÔNG CÓ", "loc": "Điều 1"}]},
    ]
    cov = golden_coverage(rows, CHUNKS, MANIFEST)
    got = {m["id"]: m["gold_chunks"] for m in cov["mapping"]}
    assert got == {"q1": ["qc#002"], "q2": ["qc#001"], "q3": ["pb#004"]}
    assert [u["id"] for u in cov["unresolved"]] == ["q5"]


def test_stats():
    s = chunk_stats(CHUNKS)
    assert s["n_chunks"] == 4 and s["n_docs"] == 2 and s["split_sections"] == 2


def test_fake_llm_answers_from_context_or_refuses():
    llm = FakeLLM()
    msg = [{"role": "user", "content": "[1] Một tín chỉ bằng 50 giờ học tập.\nCâu hỏi: tín chỉ bao nhiêu giờ?"}]
    assert llm.chat(msg).endswith("[1]")
    msg = [{"role": "user", "content": "[1] Thư viện ở tòa G.\nCâu hỏi: học phí bao nhiêu?"}]
    assert llm.chat(msg) == REFUSAL


def test_quote_picks_the_exact_chunk_and_a_wrong_quote_is_reported():
    rows = [
        {"id": "a", "citations": [{"doc_id": "pb", "loc": "mục 5", "quote": "tâm  lý HỌC đường"}]},   # case/space-insensitive
        {"id": "b", "citations": [{"doc_id": "pb", "loc": "mục 5", "quote": "giờ mở cửa"}]},
    ]
    cov = golden_coverage(rows, CHUNKS, MANIFEST)
    assert {m["id"]: m["gold_chunks"] for m in cov["mapping"]} == {"a": ["pb#004"]}
    assert [u["id"] for u in cov["unresolved"]] == ["b"]


def test_one_group_per_citation():
    rows = [{"id": "m", "citations": [{"doc_id": "qc", "loc": "Điều 25 khoản 1"}, {"doc_id": "pb", "loc": "mục 4"}]}]
    (m,) = golden_coverage(rows, CHUNKS, MANIFEST)["mapping"]
    assert m["groups"] == [["qc#001"], ["pb#003"]]
