# Retrieval — dev split

57 answerable questions (with gold chunks), 5 that must be refused.

- **R@k**: the evidence for at least one citation is in the top k.
- **Full@5**: the evidence for every citation is in the top 5 (only differs for multi-document questions).
- **MRR@10**: mean of 1/rank of the first hit.
- **refusal AUC**: how well the top-1 score alone separates answerable from unanswerable questions (0.5 = no signal).

| Chunks | Method | R@1 | R@3 | R@5 | R@10 | Full@5 | MRR@10 | refusal AUC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| structure | BM25 (syllable) | 0.63 | 0.89 | 0.93 | 0.98 | 0.86 | 0.77 | 0.71 |
| structure | BM25 (word) | 0.51 | 0.82 | 0.91 | 0.98 | 0.82 | 0.68 | 0.88 |
| structure | Dense e5-small | 0.65 | 0.84 | 0.93 | 0.96 | 0.86 | 0.76 | 0.73 |
| structure | Hybrid BM25 + e5-small | 0.77 | 0.96 | 0.98 | 0.98 | 0.91 | 0.86 | 0.83 |
| structure | Dense bge-m3 | 0.70 | 0.86 | 0.95 | 0.96 | 0.88 | 0.79 | 0.71 |
| structure | Hybrid BM25 + bge-m3 | 0.79 | 0.95 | 0.95 | 0.98 | 0.88 | 0.87 | 0.65 |
| structure | Dense vn-embedding | 0.72 | 0.96 | 0.98 | 0.98 | 0.95 | 0.83 | 0.75 |
| structure | Hybrid BM25 + vn-embedding | 0.79 | 0.96 | 0.96 | 0.98 | 0.91 | 0.88 | 0.92 |
| structure | Dense e5-base | 0.61 | 0.81 | 0.89 | 0.91 | 0.82 | 0.72 | 0.65 |
| structure | Hybrid BM25 + e5-base | 0.68 | 0.91 | 0.93 | 0.98 | 0.86 | 0.79 | 0.81 |
| structure | Hybrid BM25 + e5-small + bge-reranker-v2-m3 | 0.88 | 0.96 | 0.96 | 0.96 | 0.91 | 0.92 | 0.78 |
| structure | Hybrid BM25 + bge-m3 + bge-reranker-v2-m3 | 0.88 | 0.96 | 0.96 | 0.96 | 0.91 | 0.92 | 0.78 |
| structure | Hybrid BM25 + vn-embedding + bge-reranker-v2-m3 | 0.88 | 0.96 | 0.96 | 0.96 | 0.91 | 0.92 | 0.78 |
| structure | Hybrid BM25 + e5-base + bge-reranker-v2-m3 | 0.88 | 0.96 | 0.96 | 0.96 | 0.91 | 0.92 | 0.78 |
| structure | Hybrid BM25 + e5-small + vn-reranker | 0.77 | 0.95 | 0.96 | 0.96 | 0.89 | 0.86 | 0.78 |
| structure | Hybrid BM25 + bge-m3 + vn-reranker | 0.77 | 0.95 | 0.96 | 0.96 | 0.89 | 0.86 | 0.79 |
| structure | Hybrid BM25 + vn-embedding + vn-reranker | 0.77 | 0.95 | 0.96 | 0.96 | 0.89 | 0.86 | 0.78 |
| structure | Hybrid BM25 + e5-base + vn-reranker | 0.79 | 0.95 | 0.96 | 0.96 | 0.89 | 0.87 | 0.79 |
| fixed-300 | BM25 (syllable) | 0.56 | 0.77 | 0.84 | 0.88 | 0.74 | 0.68 | 0.57 |
| fixed-300 | BM25 (word) | 0.49 | 0.74 | 0.79 | 0.86 | 0.70 | 0.63 | 0.79 |
| fixed-300 | Dense e5-small | 0.56 | 0.74 | 0.86 | 0.89 | 0.77 | 0.67 | 0.67 |
| fixed-300 | Hybrid BM25 + e5-small | 0.65 | 0.88 | 0.91 | 0.93 | 0.84 | 0.77 | 0.73 |
| fixed-300 | Dense bge-m3 | 0.47 | 0.81 | 0.82 | 0.91 | 0.74 | 0.64 | 0.61 |
| fixed-300 | Hybrid BM25 + bge-m3 | 0.56 | 0.86 | 0.88 | 0.96 | 0.79 | 0.72 | 0.64 |
| fixed-300 | Dense vn-embedding | 0.42 | 0.77 | 0.81 | 0.89 | 0.72 | 0.60 | 0.70 |
| fixed-300 | Hybrid BM25 + vn-embedding | 0.63 | 0.79 | 0.91 | 0.96 | 0.82 | 0.74 | 0.82 |
| fixed-300 | Dense e5-base | 0.54 | 0.72 | 0.82 | 0.89 | 0.77 | 0.66 | 0.61 |
| fixed-300 | Hybrid BM25 + e5-base | 0.58 | 0.84 | 0.91 | 0.95 | 0.82 | 0.72 | 0.66 |

## Breakdown for the best method: Hybrid BM25 + e5-small + bge-reranker-v2-m3

| Group | n | R@1 | R@5 | MRR@10 |
|---|---:|---:|---:|---:|
| type=dieu_kien | 24 | 0.88 | 1.00 | 0.94 |
| type=so | 19 | 0.89 | 1.00 | 0.95 |
| type=thong_tin | 5 | 0.80 | 0.80 | 0.80 |
| type=thu_tuc | 8 | 1.00 | 1.00 | 1.00 |
| type=tinh_toan | 1 | 0.00 | 0.00 | 0.00 |
| source=shcd_quiz | 10 | 0.80 | 0.80 | 0.80 |
| source=synthetic | 47 | 0.89 | 1.00 | 0.95 |
| multi_doc=False | 56 | 0.88 | 0.96 | 0.92 |
| multi_doc=True | 1 | 1.00 | 1.00 | 1.00 |

## Misses of the best method (evidence not in top 5): 2

- `shcd11` Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  gold: qc-dao-tao · Điều 24 khoản 1  
  top 3: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 10. Học bổng dành cho sinh viên là học sinh VFIS xét tuyển vào TDTU, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 4. Học bổng dành cho tân sinh viên là học sinh xếp mức Tốt/Giỏi của trường THPT chuyên, trọng điểm
- `shcd28` Khi nào bạn nên tìm đến Chuyên viên Tâm lý của TDTU?  
  gold: phong-ban · 5. Văn phòng tư vấn và hỗ trợ sinh viên  
  top 3: phong-ban · 5. Văn phòng tư vấn và hỗ trợ sinh viên, phong-ban · CÁC KHOA VÀ TRUNG TÂM TRỰC THUỘC, thong-tin-chung · 2. Triết lý giáo dục, sứ mạng, tầm nhìn, mục tiêu

## Chunk length in model tokens

| Model | max tokens read | median | max | truncated chunks |
|---|---:|---:|---:|---:|
| e5-small | 512 | 308 | 680 | 16 |
| bge-m3 | 1024 | 306 | 678 | 0 |
| vn-embedding | 1024 | 306 | 678 | 0 |
| e5-base | 512 | 308 | 680 | 16 |
