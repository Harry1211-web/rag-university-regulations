# Retrieval — test split

85 answerable questions (with gold chunks), 9 that must be refused.

- **R@k**: the evidence for at least one citation is in the top k.
- **Full@5**: the evidence for every citation is in the top 5 (only differs for multi-document questions).
- **MRR@10**: mean of 1/rank of the first hit.
- **refusal AUC**: how well the top-1 score alone separates answerable from unanswerable questions (0.5 = no signal).

| Chunks | Method | R@1 | R@3 | R@5 | R@10 | Full@5 | MRR@10 | refusal AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| structure | BM25 (syllable) | 0.61 | 0.81 | 0.84 | 0.89 | 0.80 | 0.71 | 0.67 |
| structure | BM25 (word) | 0.59 | 0.82 | 0.85 | 0.91 | 0.80 | 0.71 | 0.76 |
| structure | Dense e5-small | 0.61 | 0.80 | 0.84 | 0.89 | 0.76 | 0.71 | 0.68 |
| structure | Hybrid BM25 + e5-small | 0.65 | 0.84 | 0.92 | 0.95 | 0.86 | 0.75 | 0.62 |
| structure | Dense bge-m3 | 0.74 | 0.85 | 0.88 | 0.92 | 0.81 | 0.80 | 0.77 |
| structure | Hybrid BM25 + bge-m3 | 0.69 | 0.86 | 0.88 | 0.95 | 0.84 | 0.79 | 0.60 |
| structure | Dense vn-embedding | 0.79 | 0.94 | 0.95 | 0.95 | 0.88 | 0.86 | 0.74 |
| structure | Hybrid BM25 + vn-embedding | 0.75 | 0.88 | 0.93 | 0.96 | 0.85 | 0.82 | 0.59 |
| structure | Dense e5-base | 0.59 | 0.72 | 0.80 | 0.92 | 0.72 | 0.68 | 0.58 |
| structure | Hybrid BM25 + e5-base | 0.61 | 0.80 | 0.88 | 0.92 | 0.85 | 0.72 | 0.55 |
| structure | Hybrid BM25 + e5-small + bge-reranker-v2-m3 | 0.86 | 0.95 | 0.95 | 0.95 | 0.92 | 0.90 | 0.74 |
| structure | Hybrid BM25 + bge-m3 + bge-reranker-v2-m3 | 0.87 | 0.95 | 0.96 | 0.98 | 0.94 | 0.92 | 0.77 |
| structure | Hybrid BM25 + vn-embedding + bge-reranker-v2-m3 | 0.87 | 0.95 | 0.98 | 0.98 | 0.95 | 0.92 | 0.74 |
| structure | Hybrid BM25 + e5-base + bge-reranker-v2-m3 | 0.86 | 0.94 | 0.96 | 0.96 | 0.93 | 0.91 | 0.77 |
| structure | Hybrid BM25 + e5-small + vn-reranker | 0.79 | 0.92 | 0.93 | 0.94 | 0.91 | 0.85 | 0.81 |
| structure | Hybrid BM25 + bge-m3 + vn-reranker | 0.80 | 0.95 | 0.95 | 0.98 | 0.92 | 0.87 | 0.82 |
| structure | Hybrid BM25 + vn-embedding + vn-reranker | 0.80 | 0.93 | 0.95 | 0.98 | 0.92 | 0.87 | 0.82 |
| structure | Hybrid BM25 + e5-base + vn-reranker | 0.80 | 0.94 | 0.94 | 0.96 | 0.91 | 0.87 | 0.81 |
| fixed-300 | BM25 (syllable) | 0.56 | 0.75 | 0.87 | 0.95 | 0.78 | 0.68 | 0.67 |
| fixed-300 | BM25 (word) | 0.59 | 0.75 | 0.85 | 0.92 | 0.78 | 0.69 | 0.77 |
| fixed-300 | Dense e5-small | 0.56 | 0.74 | 0.81 | 0.86 | 0.75 | 0.67 | 0.61 |
| fixed-300 | Hybrid BM25 + e5-small | 0.59 | 0.82 | 0.87 | 0.93 | 0.81 | 0.71 | 0.72 |
| fixed-300 | Dense bge-m3 | 0.59 | 0.79 | 0.86 | 0.91 | 0.78 | 0.70 | 0.79 |
| fixed-300 | Hybrid BM25 + bge-m3 | 0.65 | 0.86 | 0.94 | 0.96 | 0.84 | 0.76 | 0.62 |
| fixed-300 | Dense vn-embedding | 0.61 | 0.87 | 0.92 | 0.93 | 0.85 | 0.74 | 0.70 |
| fixed-300 | Hybrid BM25 + vn-embedding | 0.65 | 0.89 | 0.94 | 0.98 | 0.85 | 0.77 | 0.70 |
| fixed-300 | Dense e5-base | 0.54 | 0.76 | 0.84 | 0.91 | 0.73 | 0.67 | 0.60 |
| fixed-300 | Hybrid BM25 + e5-base | 0.62 | 0.82 | 0.92 | 0.95 | 0.87 | 0.74 | 0.75 |

## Breakdown for the best method: Hybrid BM25 + bge-m3 + bge-reranker-v2-m3

| Group | n | R@1 | R@5 | MRR@10 |
|---|---:|---:|---:|---:|
| type=dieu_kien | 28 | 0.86 | 0.96 | 0.91 |
| type=so | 34 | 0.82 | 0.94 | 0.88 |
| type=thong_tin | 11 | 1.00 | 1.00 | 1.00 |
| type=thu_tuc | 9 | 0.89 | 1.00 | 0.94 |
| type=tinh_toan | 3 | 1.00 | 1.00 | 1.00 |
| source=shcd_quiz | 14 | 0.86 | 1.00 | 0.93 |
| source=synthetic | 71 | 0.87 | 0.96 | 0.91 |
| multi_doc=False | 79 | 0.86 | 0.96 | 0.91 |
| multi_doc=True | 6 | 1.00 | 1.00 | 1.00 |

## Misses of the best method (evidence not in top 5): 3

- `q013` Phải đi học bao nhiêu phần trăm mới được thi?  
  gold: qc-dao-tao · Điều 25 khoản 1; qc-dao-tao · Điều 34  
  top 3: qd-ung-dung-cong-nghe · Điều 6 khoản 2, qd-tieng-anh-clc · Điều 3, qd-tieng-anh-clc · PHỤ LỤC 3. HÌNH THỨC ĐÁNH GIÁ VÀ ĐIỀU KIỆN XÉT ĐẠT HỌC PHẦN TIẾNG ANH
- `q019` Điểm trung bình tích lũy tối thiểu để được tốt nghiệp là bao nhiêu?  
  gold: qc-dao-tao · Điều 31 khoản 1, 2  
  top 3: qc-dao-tao · Điều 31 khoản 5, 6, qc-dao-tao · Điều 4 khoản 6, qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4
- `q115` Sinh viên có được góp ý về chất lượng giảng dạy của giảng viên không?  
  gold: quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 6. ỨNG XỬ TRONG HỌC THUẬT:  
  top 3: qc-dao-tao · Điều 10 khoản 3, 4, qc-dao-tao · Điều 10 khoản 1, 2, qd-ung-dung-cong-nghe · Điều 13 khoản 4

## Chunk length in model tokens

| Model | max tokens read | median | max | truncated chunks |
|---|---:|---:|---:|---:|
| e5-small | 512 | 308 | 680 | 16 |
| bge-m3 | 1024 | 306 | 678 | 0 |
| vn-embedding | 1024 | 306 | 678 | 0 |
| e5-base | 512 | 308 | 680 | 16 |
