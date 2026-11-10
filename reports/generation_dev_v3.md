# Generation — dev split

62 questions: 56 must be answered, 6 must be refused. Retrieval for RAG is frozen (docs/retrieval.md): top 5 chunks.

| Config | Overall | Multiple choice | Free text (judge) | False refusal | Refusal recall |
|---|---:|---:|---:|---:|---:|
| closed-api | 44% | 89% | 34% | 30% | 50% |
| rag-api | 92% | 67% | 96% | 5% | 100% |
| closed-local | 22% | 78% | 14% | 7% | 0% |
| rag-local | 73% | 89% | 72% | 0% | 50% |

- **Overall**: mean score over all questions (answerable: correct = 1, partial = 0.5; must-refuse: 1 if refused).
- **Free text**: graded by the API judge (the local judge where the API one is missing).
- **False refusal**: answerable questions the model declined. **Refusal recall**: must-refuse questions it declined.

## Citations and grounding (RAG)

| Config | Evidence in context | Cites something | Cites gold chunk | Citation precision | Invalid cite numbers | Grounded (judge) |
|---|---:|---:|---:|---:|---:|---:|
| rag-api | 96% | 100% | 100% | 86% | 0 | 98% |
| rag-local | 96% | 100% | 93% | 56% | 0 | 53% |

## Judge agreement (API judge vs local judge, same answers)

| Config | n | Same label | Cohen's kappa |
|---|---:|---:|---:|
| closed-api | 47 | 68% | 0.59 |
| rag-api | 47 | 70% | -0.02 |
| closed-local | 47 | 60% | 0.38 |
| rag-local | 47 | 64% | 0.33 |

## Errors of rag-api: 6

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd09` **over-refusal**  — Trong kỳ thi tập trung của trường, sinh viên cần làm gì nếu bị trùng lịch thi?  
  expected: Sinh viên kiểm tra lịch thi tổng hợp, nếu các môn học bị trùng lịch thi có lịch thi khác và không trùng với lịch thi của sinh viên, sinh viên nộp đơn Chuyển giờ thi. Nếu các môn học bị trùng lịch khôn  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd11` **over-refusal (evidence missing)**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd28` **over-refusal (evidence missing)**  — Khi nào bạn nên tìm đến Chuyên viên Tâm lý của TDTU?  
  expected: Khi cảm thấy áp lực, lo âu, khó thích nghi, gặp biến cố hoặc đơn giản muốn có người lắng nghe.  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `q034` **generation** (api: incorrect, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết là môn A mà sinh viên bắt buộc phải **đăng ký học và đạt** trước khi đăng ký môn B.[1] Văn bản hiện có chỉ nhắc “môn học trước” là một điều kiện ràng buộc khi đăng ký môn học, nhưng không nêu định nghĩa cụ thể; vì vậy chưa đủ căn cứ để  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5, qc-dao-tao · Điều 13 khoản 1, 2
- `q040` **generation** (api: partial, local: correct) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Vắng thi không phép bị ghi điểm V, tính như điểm 0; đồng thời được xem là đã dự thi một lần. [2][4]  
  cited: qc-dao-tao · Điều 23, qc-dao-tao · Điều 24 khoản 2
- `q055` **generation** (api: partial, local: correct) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh yêu cầu IELTS từ **5.5**, với từng kỹ năng đạt ít nhất **4.5**. [1]  
  cited: qd-tieng-anh-clc · PHỤ LỤC 4. CHUẨN ĐẦU RA TIẾNG ANH

Causes: generation 3, over-refusal (evidence missing) 2, over-refusal 1

## Errors of rag-local: 26

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd05` **hallucination**  — Sơ đồ đào tạo và sơ đồ tích lũy có giống nhau không?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b **Giải thích:** Các văn bản hiện có quy định về cấu trúc chương trình đào tạo (bao gồm khối lượng học tập chung/r riêng, môn bắt buộc/tự chọn, tỷ lệ lý thuyết/thực hành) và các điều kiện ràng buộc như lộ trình học tiếng Anh, điều kiện tiên   
  cited: qc-dao-tao · Điều 2 khoản 1, 2, 3, qd-tieng-anh-clc · Điều 5, qc-dao-tao · Điều 15, qc-dao-tao · Điều 3 khoản 1, 2
- `shcd11` **retrieval**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Đáp án: c Giải thích: Theo quy định tính điểm môn học trong văn bản hiện có, điểm môn học được tính bằng tổng các thành phần (Quá trình, Giữa kỳ, Cuối kỳ) nhân với tỷ trọng tương ứng của từng thành phần đó [4]. Tuy nhiên, các đoạn trích đã cung cấp c  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế
- `shcd17` **hallucination**  — Sinh viên xem thông báo đóng học phí ở đâu?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: a **Giải thích:** Theo quy định trong văn bản [1], Phòng Tài chính có trách nhiệm thông báo học phí, thời gian nộp và hướng dẫn cách thức nộp cho sinh viên. Tuy nhiên, các đoạn trích hiện có **không nêu rõ** địa điểm cụ thể (như "Cổng thông t  
  cited: qc-dao-tao · Điều 35, phong-ban · 8. Phòng Tài chính, qd-tap-su · Điều 7, qc-dao-tao · Điều 30, qc-dao-tao · Điều 13 khoản 3
- `shcd26` **hallucination**  — Nguyên tắc ứng xử của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b Giải thích: Theo đoạn trích [1], mục tiêu của Bộ Quy tắc ứng xử là tạo lập môi trường học tập, nghiên cứu "bình đẳng, công bằng, văn minh và hiệu quả". Tuy nhiên, khi xem xét các lựa chọn trong đề bài, chỉ có lựa chọn **b** ("Giáo dục, nghi  
  cited: quy-tac-ung-xu · I. MỤC TIÊU VÀ NGUYÊN TẮC:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 7. TÔN TRỌNG QUYỀN SỞ HỮU TRÍ TUỆ:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 6. ỨNG XỬ TRONG HỌC THUẬT:
- `q003` **generation** (api: partial, local: correct) — Học kỳ chính phải đăng ký ít nhất bao nhiêu tín chỉ?  
  expected: 10 tín chỉ, trừ học kỳ cuối khóa và sinh viên chưa đạt trình độ tiếng Anh theo quy định.  
  got: Học kỳ chính phải đăng ký ít nhất **10 tín chỉ**. Tuy nhiên, mức tối thiểu này có các ngoại lệ và điều kiện cụ thể như sau: * Ngoại lệ cho sinh viên không đạt trình độ tiếng Anh quy định tại Điều 12 khoản 1 điểm b: Sinh viên này bị hạn chế số tín chỉ  
  cited: qc-dao-tao · Điều 12, qc-dao-tao · Điều 13 khoản 4, 5, 7
- `q016` **generation** (api: incorrect, local: partial) — 6,9 điểm là C+ hay B?  
  expected: C+ (2.5 hệ 4), vì B bắt đầu từ 7,0.  
  got: Đáp án: Không thể xác định chính xác là C+ hay B dựa trên các văn bản hiện có. Các văn bản cung cấp thang điểm hệ 10 và cách chuyển đổi sang hệ 4 hoặc điểm chữ tương ứng, nhưng không nêu rõ quy tắc cụ thể để phân biệt giữa "C+" và "B" khi chỉ biết đi  
  cited: qc-dao-tao · Điều 24 khoản 1, qc-dao-tao · Điều 26 khoản 3, 4, qc-ren-luyen · Điều 9, qc-dao-tao · Điều 31 khoản 5, 6, qc-ren-luyen · Điều 4
- `q029` **generation** (api: partial, local: partial) — Học kỳ đầu GPA bao nhiêu thì bị cảnh báo?  
  expected: ĐTBHK dưới 2,00 với học kỳ đầu của khóa học.  
  got: GPA (điểm trung bình chung) dưới **2,00** đối với học kỳ đầu của khóa học sẽ khiến sinh viên bị cảnh báo kết quả học tập. Điều kiện cụ thể để áp dụng mức điểm này là: - Sinh viên phải còn trong thời hạn khóa học và không thuộc trường hợp trễ tiến độ   
  cited: qc-dao-tao · Điều 17 khoản 1, qc-dao-tao · Điều 17 khoản 2, 3, 4
- `q034` **generation** (api: partial, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết và môn học trước khác nhau ở điều kiện bắt buộc để đăng ký học môn học đó, cụ thể như sau: 1. **Điều kiện của môn tiên quyết:** Để được phép đăng ký học môn B, sinh viên bắt buộc phải đã đăng ký học và đạt môn A (theo thang điểm đánh g  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5, qc-dao-tao · Điều 13 khoản 1, 2
- `q036` **generation** (api: partial, local: correct) — Rớt một môn tự chọn có bắt buộc phải học lại không?  
  expected: Không bắt buộc nếu đã tích lũy đủ số tín chỉ của nhóm tự chọn; có thể học lại môn đó hoặc chọn môn tự chọn khác cùng nhóm.  
  got: Không, sinh viên không bắt buộc phải học lại môn tự chọn nếu đã tích lũy đủ số tín chỉ của nhóm môn học tự chọn tương ứng [1]. Tuy nhiên, nếu chưa đạt điểm yêu cầu để được tính vào trung bình chung hoặc muốn cải thiện kết quả, sinh viên có quyền đăng  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 3 khoản 1, 2, qc-dao-tao · Điều 15, tb-ha-bac-tot-nghiep · (không có mục)
- `q040` **generation** (api: partial, local: correct) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Vắng thi không phép được ghi nhận là "Điểm V" (tương đương với "Không đủ điều kiện dự thi"), có giá trị tính như điểm 0 và được tính vào điểm trung bình học kỳ cũng như điểm trung bình tích lũy [4]. Các quy định liên quan bao gồm: - Sinh viên vắng th  
  cited: qc-dao-tao · Điều 25 khoản 5, 6, qc-dao-tao · Điều 23, qc-dao-tao · Điều 24 khoản 2, qd-tieng-anh-clc · Điều 3
- `q042` **generation** (api: partial, local: partial) — Muốn bảo lưu vì lý do cá nhân thì cần điều kiện gì?  
  expected: Đã học tối thiểu 01 học kỳ, không thuộc diện bị xem xét buộc thôi học hoặc kỷ luật, ĐTBTL không dưới 5,00; thời gian nghỉ vẫn tính vào thời gian học tối đa.  
  got: Để sinh viên được xin nghỉ học tạm thời và bảo lưu kết quả vì lý do cá nhân, cần đáp ứng các điều kiện sau: phải thực hiện nghĩa vụ đóng học phí cho môn học còn nợ (trừ khi nộp đơn trước 02 tuần thì không phải đóng); phải đạt điểm trung bình chung tí  
  cited: qc-dao-tao · Điều 16 khoản 3, 4, qc-dao-tao · Điều 16 khoản 1, 2, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 3. Nguyên tắc xét cấp học bổng:, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường, hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 4. Lưu ý:
- `q053` **generation** (api: partial, local: partial) — Bị trùng lịch thi hai môn thì xin hoãn thi thế nào?  
  expected: Nộp đơn Hoãn thi trong thời gian quy định được công bố cùng lịch thi để được ghi nhận điểm H.  
  got: Để xin hoãn thi khi bị trùng lịch thi hai môn, sinh viên phải thực hiện các bước và đáp ứng điều kiện sau dựa trên quy định hiện hành: 1. **Nộp đơn:** Sinh viên phải nộp đơn "Hoãn thi" trong thời gian quy định được công bố cùng với lịch thi [1]. 2. *  
  cited: qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 23
- `q055` **generation** (api: partial, local: partial) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh cần IELTS từ **≥ 5.5** (tất cả kỹ năng ≥ 4.5) để đạt yêu cầu tối thiểu của sinh viên [2]. Tuy nhiên, mức điểm này có thể thấp hơn hoặc cao hơn tùy thuộc vào mục đích cụ thể: * Để được xét miễn học phần Tiếng Anh theo chương trì  
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú, hd-hoc-bong · VII. KHEN THƯỞNG > A. TẶNG GIẤY KHEN:, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ
- `q056` **generation** (api: partial, local: correct) — Học bổng khuyến khích cần GPA bao nhiêu?  
  expected: Điểm trung bình tích lũy các môn ngành chính (điểm thi lần 1, không tính môn cải thiện) trong kỳ/năm xét từ loại Khá (7.0) trở lên; kèm điểm rèn luyện từ 65, không có môn dưới 5.0, không thi lại lần 2  
  got: Học bổng khuyến khích cần điểm trung bình tích lũy (GPA) từ loại Khá tương ứng với **7.0** trở lên đối với sinh viên năm thứ nhất [2] và sinh viên từ năm thứ 2 trở lên [1]. Ngoài ra, sinh viên còn phải đạt điểm rèn luyện từ loại Khá tương ứng với **6  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q057` **generation** (api: partial, local: partial) — Điểm rèn luyện toàn khóa tối thiểu bao nhiêu thì được tốt nghiệp?  
  expected: Điểm rèn luyện trung bình toàn khóa phải từ 50 điểm trở lên.  
  got: Điểm rèn luyện toàn khóa tối thiểu để xét tốt nghiệp là **50 điểm** (tương đương trung bình tích lũy toàn khóa từ 5,00 đến dưới 6,00 theo bảng xếp loại), áp dụng cho sinh viên Khóa tuyển sinh năm 2017 trở về sau. Các điều kiện và quy định liên quan b  
  cited: qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4, qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8, qc-dao-tao · Điều 31 khoản 1, 2
- `q064` **generation** (api: incorrect, local: partial) — Điểm rèn luyện được chấm theo mấy nội dung, mỗi nội dung tối đa bao nhiêu điểm?  
  expected: 6 nội dung (học tập và học thuật; chấp hành nội quy; hoạt động chính trị - xã hội, văn hóa, thể thao; hoạt động cộng đồng, tình nguyện; tinh thần tiên phong, gương mẫu; điểm thưởng), mỗi nội dung tối   
  got: Điểm rèn luyện được chấm theo **7 nội dung**, mỗi nội dung có mức điểm tối đa là **20 điểm**. Các nội dung và điều kiện cụ thể như sau: 1. **Việc tham gia học tập và các hoạt động chuyên môn học thuật:** Tối đa 20 điểm, trong đó nếu xếp loại Kém hoặc  
  cited: qc-ren-luyen · Điều 3, qc-ren-luyen · Điều 10 khoản 2, 3, 4, qc-ren-luyen · Điều 10 khoản 1, qc-ren-luyen · Điều 8, qc-ren-luyen · Điều 4
- `q067` **generation** (api: partial, local: partial) — Bị xếp loại rèn luyện yếu hai học kỳ liên tiếp thì sao?  
  expected: Phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo; nếu bị yếu, kém hai học kỳ liên tiếp lần thứ hai thì bị buộc thôi học (ngoại lệ do Hội đồng quyết định).  
  got: Nếu sinh viên bị xếp loại rèn luyện yếu trong hai học kỳ liên tiếp, họ sẽ bị buộc thôi học [1]. Tuy nhiên, quy định này có các ngoại lệ và thủ tục cụ thể như sau: * **Quy định chung:** Sinh viên bị xếp loại rèn luyện yếu, kém trong hai học kỳ liên ti  
  cited: qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8, qc-dao-tao · Điều 17 khoản 2, 3, 4
- `q071` **generation** (api: partial, local: partial) — Khối lượng học tập được công nhận và chuyển đổi tín chỉ tối đa là bao nhiêu?  
  expected: Với chương trình đại học: không vượt quá 50% khối lượng học tập của chương trình đào tạo đang học.  
  got: Khối lượng học tập được công nhận và chuyển đổi tín chỉ tối đa phụ thuộc vào trình độ đào tạo đang học, cụ thể như sau: * Đối với chương trình đào tạo đại học (CTĐT đại học): Tối đa không vượt quá 50% khối lượng học tập của CTĐT đang học [1][2]. * Đố  
  cited: qc-dao-tao · Điều 28, qd-cong-nhan-tin-chi · Điều 3
- `q078` **generation** (api: partial, local: partial) — Không học Ngôn ngữ Anh thì cần IELTS bao nhiêu để được Cử nhân ưu tú?  
  expected: IELTS ≥ 5.5 (hoặc PET/FCE ≥ 160, TOEFL iBT ≥ 50; TOEIC Nghe & Đọc ≥ 600).  
  got: Để được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú khi không học chuyên ngành Ngôn ngữ Anh, sinh viên thuộc các ngành khác phải đạt mức điểm IELTS tối thiểu là 5.5 [1]. Ngoài ra, đối với sinh viên chương trình chất lượng cao khóa tuyển sinh từ năm 2017   
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú
- `q086` **generation** (api: partial, local: correct) — Học lực Xuất sắc nhưng rèn luyện chỉ Khá thì nhận học bổng loại gì?  
  expected: Học bổng loại Khá.  
  got: Sinh viên có học lực Xuất sắc nhưng rèn luyện chỉ Khá sẽ được xét cấp **Học bổng loại Khá**. Theo quy định, để đạt Học bổng loại Khá, sinh viên cần thỏa mãn các điều kiện: Kết quả học tập là Xuất sắc (hoặc Giỏi) và Kết quả rèn luyện từ Khá trở lên [1  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 3. Nguyên tắc xét cấp học bổng:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q088` **generation** (api: partial, local: partial) — Hai anh em ruột cùng học ở trường thì có học bổng không?  
  expected: Có: 15% học phí theo khung chương trình tiêu chuẩn mỗi năm học, áp dụng từ người thứ hai; cấp vào cuối năm học.  
  got: Có, hai anh em ruột cùng học tại Trường Đại học Tôn Đức Thắng (TDTU) sẽ được xét cấp học bổng nếu thỏa mãn các điều kiện cụ thể sau: 1. **Đối tượng áp dụng:** Học bổng dành cho anh/chị em ruột đang học ngành chính tại Trường theo đúng khóa học [1]. 2  
  cited: hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường, hd-hoc-bong · V. HỌC BỔNG ÁP DỤNG CHO PHÂN HIỆU > 3. Học bổng dành cho sinh viên là con ruột/em ruột của cựu sinh viên TDTU, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học
- `q099` **generation** (api: partial, local: partial) — Chương trình kỹ sư chất lượng cao có mấy học phần tiếng Anh?  
  expected: 05 học phần tiếng Anh dự bị ngoài chương trình và 05 học phần tiếng Anh chính thức.  
  got: Chương trình kỹ sư chất lượng cao gồm tổng cộng **09** học phần tiếng Anh, bao gồm 05 học phần dự bị và 04 học phần chính thức. Cụ thể: 1. **Học phần dự bị:** Gồm 05 học phần (Tiếng Anh dự bị 1, 2, 3, 4, 5) thuộc chương trình dự bị tập trung [3][4].   
  cited: qd-tieng-anh-clc · Điều 2 khoản 1, 2, 3, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY, qd-tieng-anh-clc · Điều 2 khoản 4
- `q104` **generation** (api: incorrect, local: partial) — Đi thi trễ bao lâu thì không được vào phòng?  
  expected: Sau 15 phút kể từ khi tính giờ làm bài.  
  got: Đáp án: Không có lựa chọn cụ thể nào trong đề bài để trả lời trực tiếp, vì các phương án chưa nêu rõ thời gian cụ thể. Theo văn bản hiện có, quy định về việc đi thi trễ như sau: - Thí sinh phải có mặt tại phòng thi trước giờ thi 30 phút [2]. - Trường  
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh, phu-luc-vi-pham · (không có mục)
- `q107` **generation** (api: partial, local: correct) — Nhìn bài bạn trong giờ thi bị trừ bao nhiêu điểm?  
  expected: Trừ 25% số điểm thi (mức 1).  
  got: Vi phạm hành vi nhìn bài của thí sinh khác trong giờ thi sẽ bị trừ **25% số điểm thi** (Mức 1) nếu đây là lần đầu tiên vi phạm; hoặc bị **trừ 50% số điểm thi** (Mức 2) nếu đã từng bị xử lý ở mức 1 một lần trong cùng môn thi đó và tiếp tục vi phạm. Cá  
  cited: noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh, phu-luc-vi-pham · (không có mục)
- `q112` **generation** (api: partial, local: partial) — Uống bia trong trường bị kỷ luật gì?  
  expected: Lần 1 cảnh cáo, lần 2 cảnh cáo lần 2, lần 3 đình chỉ học tập có thời hạn, lần 4 buộc thôi học.  
  got: Uống bia trong trường bị xử lý từ cảnh cáo đến buộc thôi học tùy thuộc vào số lần vi phạm tính trong cả khóa học, cụ thể như sau: Lần 1 và Lần 2 là Cảnh cáo; Lần 3 là Đình chỉ học tập có thời hạn; Lần 4 là Buộc thôi học [1]. Ngoài ra, nếu hành vi sử   
  cited: phu-luc-vi-pham · (không có mục)
- `q113` **generation** (api: incorrect, local: partial) — Bị trừ 25% điểm thi lần đầu thì có bị kỷ luật thêm không?  
  expected: Có: nghiêm khắc phê bình (lần 1), khiển trách (lần 2), ... đến buộc thôi học (lần 6).  
  got: Đáp án: Không có thông tin cụ thể về việc "bị kỷ luật thêm" khi chỉ bị trừ 25% điểm thi lần đầu trong các văn bản hiện có. Các điều kiện và quy định liên quan được nêu như sau: - Mức xử lý vi phạm nội quy phòng thi (trừ 25% điểm) là mức thấp nhất, kh  
  cited: phu-luc-vi-pham · (không có mục), noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:

Causes: generation 22, hallucination 3, retrieval 1

