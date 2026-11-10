# Chunk statistics

Settings: max_words=300, min_words=50 (words = whitespace tokens, i.e. Vietnamese syllables)

- Documents: 18
- Chunks: 337 (86 contain table rows; 208 come from sections that had to be split)
- Words per chunk (body, without the context header): min 22, p10 96, median 216, p90 289, max 376; total 68029

| Document | Chunks |
|---|---:|
| hd-hoc-bong | 79 |
| qc-dao-tao | 65 |
| qc-ren-luyen | 31 |
| qd-ung-dung-cong-nghe | 31 |
| qd-tieng-anh-clc | 18 |
| phu-luc-vi-pham | 18 |
| qd-cong-nhan-tin-chi | 16 |
| phong-ban | 16 |
| quy-tac-ung-xu | 12 |
| noi-quy-phong-thi | 11 |
| hd-giao-tiep | 10 |
| qd-tap-su | 7 |
| qd-cu-nhan-uu-tu | 5 |
| dk-thu-khen | 5 |
| dac-diem-nhan-dien | 5 |
| ct-3-noi-dung-dao-duc | 4 |
| tb-ha-bac-tot-nghiep | 2 |
| thong-tin-chung | 2 |

## Golden-set coverage

Every citation in `eval/golden.jsonl` is mapped to the chunk(s) that contain it.

| Source | Split | Questions | Must answer | Resolved to chunks | Must refuse |
|---|---|---:|---:|---:|---:|
| shcd_quiz | dev | 12 | 9 | 9 | 3 |
| shcd_quiz | test | 18 | 14 | 14 | 4 |
| synthetic | dev | 50 | 47 | 47 | 3 |
| synthetic | test | 76 | 71 | 71 | 5 |

Answerable questions without a gold chunk: none

