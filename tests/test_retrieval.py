import numpy as np

from src.rag.baseline import fixed_size_chunks, map_gold
from src.rag.embed import HashEmbedder
from src.rag.metrics import covers_all, evaluate, first_hit, refusal_auc
from src.rag.retrieve import BM25, dense_scores, rerank, rrf, tok_syllable, tok_word, top

DOCS = [
    "Sinh viên vắng thi có phép được nhận điểm H và thi lại trong năm học kế tiếp.",
    "Học bổng khuyến khích học tập xét theo điểm trung bình và điểm rèn luyện.",
    "Thư viện nằm ở tòa nhà G, mở cho toàn bộ sinh viên.",
]
IDS = ["a", "b", "c"]


def test_tokenizers():
    assert tok_syllable("Học bổng, ĐIỂM H.") == ["học", "bổng", "điểm", "h"]
    assert "học_bổng" in tok_word("Học bổng khuyến khích học tập")


def test_bm25_ranks_the_matching_chunk_first():
    bm = BM25([tok_syllable(d) for d in DOCS])
    assert top(IDS, bm.scores(tok_syllable("vắng thi có phép thì sao"), ), 3)[0][0] == "a"
    assert top(IDS, bm.scores(tok_syllable("học bổng")), 1)[0][0] == "b"
    assert not bm.scores(tok_syllable("ký túc xá")).any()        # no shared term -> all zero


def test_rare_terms_weigh_more_than_common_ones():
    bm = BM25([tok_syllable(d) for d in DOCS])
    common, rare = bm.idf[bm.vocab["sinh"]], bm.idf[bm.vocab["thư"]]
    assert rare > common


def test_dense_with_hash_embedder():
    emb = HashEmbedder()
    v = emb.encode(DOCS)
    assert np.allclose(np.linalg.norm(v, axis=1), 1)
    q = emb.encode(["thư viện ở tòa nào"], "query")[0]
    assert top(IDS, dense_scores(v, q), 1)[0][0] == "c"


def test_rrf_rewards_agreement():
    fused = [c for c, _ in rrf([["x", "a", "b"], ["y", "a", "c"]])]
    assert fused[0] == "a"


def test_rerank_orders_by_score_and_keeps_unscored_last():
    assert [c for c, _ in rerank(["a", "b", "c"], {"a": 0.1, "c": 0.9})] == ["c", "a", "b"]


def test_metrics():
    gold = {"q1": [["a"]], "q2": [["b"], ["c"]], "q3": [["z"]]}
    runs = {"q1": ["a", "b"], "q2": ["c", "x", "y", "w", "b"], "q3": ["a", "b"]}
    assert first_hit(runs["q2"], gold["q2"]) == 1
    assert covers_all(runs["q2"], gold["q2"], 5) and not covers_all(runs["q2"], gold["q2"], 4)
    m = evaluate(runs, gold)
    assert m["n"] == 3 and abs(m["R@1"] - 2 / 3) < 1e-9 and abs(m["Full@5"] - 2 / 3) < 1e-9
    assert refusal_auc({"q1": 0.9, "q2": 0.8, "r": 0.1}, {"q1": True, "q2": True, "r": False}) == 1.0


def test_fixed_windows_and_gold_mapping():
    words = [f"w{i}" for i in range(700)]
    chunks = [{"id": "d#001", "doc_id": "d", "text": " ".join(words[:350])},
              {"id": "d#002", "doc_id": "d", "text": " ".join(words[350:])}]
    win = fixed_size_chunks(chunks, size=300, overlap=50)
    assert [w["id"] for w in win] == ["d~001", "d~002", "d~003"]
    assert win[1]["text"].split()[0] == "w250"                   # 50 words of overlap
    golden = [{"id": "q", "citations": [{"doc_id": "d", "loc": "x", "quote": "w600 w601 w602"}]},
              {"id": "p", "citations": [{"doc_id": "d", "loc": "y"}]}]
    m = map_gold(golden, {"q": [["d#002"]], "p": [["d#001"]]}, chunks, win)
    assert m["q"] == [["d~003"]]                                 # the window that contains the quote
    assert m["p"] == [["d~001"]]      # d~002 shares only 100 of its 300 words with d#001: below the 50% bar
