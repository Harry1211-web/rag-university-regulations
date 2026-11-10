import json

from src.rag.llm import REFUSAL, FakeLLM
from src.rag.pipeline import build_messages, judge_messages, parse_answer, parse_judge

CHUNKS = [
    {"id": "qc#025", "context": "Văn bản: Quy chế đào tạo\nMục: Điều 25", "text": "Sinh viên vắng thi có phép nhận điểm H."},
    {"id": "pb#009", "context": "Văn bản: Phòng ban\nMục: 9. Thư viện", "text": "Thư viện ở tòa nhà G."},
]
MCQ = {"question": "Vắng thi có phép thì nhận điểm gì?", "options": {"a": "F", "b": "H"}, "answer": "điểm H"}


def test_rag_prompt_numbers_excerpts_and_lists_options():
    sys_msg, user = build_messages(MCQ, CHUNKS)
    assert "CHỈ dựa trên" in sys_msg["content"]
    assert user["content"].startswith("Các đoạn trích:\n\n[1] (Quy chế đào tạo | Điều 25)\nSinh viên vắng thi")
    assert "[2] (Phòng ban | 9. Thư viện)" in user["content"]
    assert user["content"].endswith("Các lựa chọn:\na. F\nb. H")


def test_closed_book_prompt_has_no_excerpts():
    sys_msg, user = build_messages(MCQ, None)
    assert "hiểu biết của bạn" in sys_msg["content"] and "[1]" not in user["content"]


def test_parse_answer():
    p = parse_answer("Đáp án: b\nVắng thi có phép được nhận điểm H [1]. Xem thêm [1][3].", n_ctx=2)
    assert p.option == "b" and p.cited == [1] and p.invalid_cites == [3] and not p.refused
    assert parse_answer(REFUSAL, 5).refused
    assert parse_answer("Theo [1, 2], sinh viên ...", 5).cited == [1, 2]
    long = "Học phí: Không tìm thấy trong các văn bản hiện có. " + "Tuy nhiên điều kiện học bổng là ... " * 10
    assert not parse_answer(long, 5).refused          # a partial answer that mentions the gap is an answer
    explained = REFUSAL + " Các đoạn trích chỉ nói về học bổng và ký túc xá ở phân hiệu. " * 6
    assert parse_answer(explained, 5).refused         # opens with the refusal, then explains: still a refusal


def test_judge_roundtrip():
    msgs = judge_messages(MCQ, "Điểm H [1]", CHUNKS)
    assert "Reference answer:\nđiểm H" in msgs[1]["content"] and "[2] Thư viện" in msgs[1]["content"]
    assert parse_judge('```json\n{"correctness": "Correct", "grounded": "yes", "reason": "ok"}\n```')["correctness"] == "correct"
    assert parse_judge("not json")["correctness"] == "invalid"


def test_fake_llm_cites_or_refuses_and_judges():
    llm = FakeLLM()
    assert llm.chat(build_messages({"question": "vắng thi có phép"}, CHUNKS)).endswith("[1]")
    assert llm.chat(build_messages({"question": "học phí bao nhiêu"}, CHUNKS)) == REFUSAL
    assert json.loads(llm.chat([{"role": "user", "content": "x"}], json_mode=True))["correctness"] == "correct"
