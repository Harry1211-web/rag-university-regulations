# Generation — test split

94 questions: 85 must be answered, 9 must be refused. Retrieval for RAG is frozen (docs/retrieval.md): top 5 chunks.

| Config | Overall | Multiple choice | Free text (judge) | False refusal | Refusal recall |
|---|---:|---:|---:|---:|---:|
| closed-api | 41% | 71% | 37% | 31% | 22% |
| rag-api | 93% | 71% | 99% | 5% | 78% |
| closed-local | 20% | 50% | 17% | 1% | 0% |
| rag-local | 73% | 86% | 76% | 1% | 33% |

- **Overall**: mean score over all questions (answerable: correct = 1, partial = 0.5; must-refuse: 1 if refused).
- **Free text**: graded by the API judge (the local judge where the API one is missing).
- **False refusal**: answerable questions the model declined. **Refusal recall**: must-refuse questions it declined.

## Citations and grounding (RAG)

| Config | Evidence in context | Cites something | Cites gold chunk | Citation precision | Invalid cite numbers | Grounded (judge) |
|---|---:|---:|---:|---:|---:|---:|
| rag-api | 98% | 100% | 96% | 86% | 0 | 99% |
| rag-local | 98% | 100% | 95% | 68% | 1 | 51% |

## Judge agreement (API judge vs local judge, same answers)

| Config | n | Same label | Cohen's kappa |
|---|---:|---:|---:|
| closed-api | 71 | 77% | 0.70 |
| rag-api | 70 | 79% | -0.03 |
| closed-local | 71 | 75% | 0.53 |
| rag-local | 71 | 59% | 0.17 |

## Errors of rag-api: 7

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd13` **over-refusal**  — Hoạt động nào dưới đây thuộc Văn phòng Tâm lý học đường TDTU?  
  expected: Tham vấn cá nhân, sinh hoạt nhóm, yoga, thiền, Câu lạc bộ Sức khỏe Tâm lý, Cẩm nang Sức khỏe Tâm lý, Tuần lễ Sức khỏe Tinh thần và các hoạt động truyền thông.  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd16` **over-refusal**  — Sinh viên trễ lộ trình tiếng Anh, quên không thi cuối kỳ môn Tiếng Anh 1 thì có được nộp chứng chỉ tiếng Anh quốc tế để xét miễn không?  
  expected: Được nếu sinh viên học tiếng Anh liên tục trong các học kỳ chính và không bị điểm F môn Tiếng Anh ở bất kỳ lần học nào.  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd19` **over-refusal**  — Sinh viên phải làm gì để không ảnh hưởng đến điểm trung bình tốt nghiệp khi đã hoàn thành nhóm tự chọn nhưng có môn học trong nhóm tự chọn có điểm không đạt (do đã chọn học môn học khác trong nhóm tự chọn)?  
  expected: Nộp đơn đề nghị không tính điểm môn học đó vào Trung bình chung tích lũy vào học kì cuối của khóa học hoặc theo kế hoạch xét công nhận tốt nghiệp của đợt mà sinh viên đăng ký bằng cách nộp đơn trực tu  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd29` **over-refusal**  — Làm sao để biết chứng chỉ tiếng Anh của mình được xét miễn đến học phần tiếng Anh nào? Chuẩn đầu ra của từng loại chứng chỉ? (chọn câu trả lời đúng nhất)  
  expected: Sinh viên xem quy định tiếng Anh của khóa mình trên Cổng thông tin sinh viên, phân hệ Quy chế - Quy định.  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `q069` **generation** (api: partial, local: correct) — Học phần tập sự nghề nghiệp đã học ở trường khác có được công nhận để miễn không?  
  expected: Không. Các học phần tốt nghiệp/khóa luận, tập sự nghề nghiệp và một số học phần ngành do Hội đồng Khoa xác định không được công nhận để miễn học phần (ngoại lệ do Hiệu trưởng phê duyệt).  
  got: Không. Học phần tập sự nghề nghiệp không được công nhận kết quả học tập hoặc chuyển đổi tín chỉ để miễn học phần, kể cả khi đã học ở trường khác. [1]  
  cited: qd-cong-nhan-tin-chi · Điều 3
- `q122` **hallucination**  — Ở ký túc xá trường giá bao nhiêu một tháng?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Trong các văn bản hiện có, mức thu tại Ký túc xá Phân hiệu Khánh Hòa là **100.000 đồng/tháng** ở Ký túc xá cũ và **200.000 đồng/tháng** ở Ký túc xá mới, chưa gồm tiền điện nước tính theo mức sử dụng thực tế. [1] Văn bản không nêu giá Ký túc xá ở các   
  cited: hd-hoc-bong · IX. HỖ TRỢ NGƯỜI HỌC > 2. Hỗ trợ một phần chi phí Ký túc xá tại Phân hiệu Khánh Hòa
- `q124` **hallucination**  — Điểm rèn luyện bao nhiêu thì được xét kết nạp Đảng?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Kết quả đánh giá rèn luyện là một tiêu chí để xét kết nạp Đảng, nhưng các văn bản hiện có không nêu mức điểm cụ thể cần đạt. [1]  
  cited: qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4

Causes: over-refusal 4, hallucination 2, generation 1

## Errors of rag-local: 34

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd04` **generation**  — Sinh viên A vì lý do cá nhân nên đã xin nghỉ học tạm thời 1 năm học (2 học kỳ chính). Theo Anh/Chị sinh viên A này còn lại bao nhiêu thời gian để hoàn thành các môn trong chương trình học? (Sinh viên A học chương trình có thời gian đào tạo chính thức 4 năm).  
  expected: 6 năm. Tối đa 7 năm nhưng sinh viên đã nghỉ 1 năm vì lý do cá nhân.  
  got: Đáp án: c **Giải thích:** - Thời gian đào tạo chính thức cho chương trình 4 năm là từ 04 đến 05 năm học [2]. - Thời gian tối đa hoàn thành bao gồm thời gian theo kế hoạch cộng thêm 6 học kỳ (tương đương 1,5 năm) đối với khóa học 4 năm [2]. Do đó, thờ  
  cited: qc-dao-tao · Điều 16 khoản 1, 2, qc-dao-tao · Điều 5
- `shcd06` **hallucination**  — Thời gian thu học phí của các học kỳ trong năm học được thông báo đến sinh viên qua những kênh nào? Chọn câu đúng nhất.  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: d Giải thích: Theo quy định, kế hoạch giảng dạy và học tập (trong đó có các mốc thời gian chính của hoạt động đào tạo) được công bố kịp thời tới các bên liên quan trước khi bắt đầu năm học [3]. Đồng thời, sinh viên phải thường xuyên kiểm tra   
  cited: qd-ung-dung-cong-nghe · Điều 13 khoản 1, qc-dao-tao · Điều 6 khoản 1, 2, 3, phong-ban · 8. Phòng Tài chính
- `shcd08` **hallucination**  — Giá trị cốt lõi của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b Giải thích: Theo đoạn trích [1], sứ mạng của Trường Đại học Tôn Đức Thắng là "Giáo dục, nghiên cứu và sáng tạo vì sự phát triển toàn diện của con người và xã hội". Đây chính là nội dung mô tả giá trị cốt lõi trong các lựa chọn đã cho. Các l  
  cited: thong-tin-chung · 2. Triết lý giáo dục, sứ mạng, tầm nhìn, mục tiêu
- `shcd12` **hallucination**  — Khẩu hiệu của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: c Giải thích: Khẩu hiệu của Trường Đại học Tôn Đức Thắng là "Giáo dục, nghiên cứu và sáng tạo vì sự phát triển toàn diện của con người và xã hội". Các lựa chọn khác không phải là khải hiệu mà là các thành phần khác trong sứ mạng hoặc tầm nhìn  
  cited: thong-tin-chung · 2. Triết lý giáo dục, sứ mạng, tầm nhìn, mục tiêu, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 7. TÔN TRỌNG QUYỀN SỞ HỮU TRÍ TUỆ:
- `shcd14` **hallucination**  — Sinh viên có thể xem Sơ đồ đào tạo ở đâu?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: Không thể xác định được lựa chọn đúng dựa trên các văn bản hiện có. Các văn bản cung cấp đã đề cập đến việc xem "bảng điểm đánh giá" hoặc "bảng tổng hợp" có thông tin về "số tín chỉ tích lũy" trên "Cổng thông tin sinh viên" [1], cũng như yêu   
  cited: qc-dao-tao · Điều 30, qc-dao-tao · Điều 31 khoản 1, 2
- `shcd30` **generation**  — Sơ đồ đào tạo thể hiện môn A là môn song hành của môn B nghĩa là gì?  
  expected: Sinh viên có thể đăng ký học môn A và B trong cùng một học kỳ hoặc có thể đăng ký môn A học trước. Tuy nhiên, sinh viên không thể đăng ký học môn B trước khi đăng ký học môn A.  
  got: Đáp án: a Giải thích: Theo quy định tại khoản f Điều 4 Quy chế tổ chức và quản lý đào tạo trình độ đại học [1], môn học song hành là trường hợp sinh viên được phép đăng ký học môn B vào cùng học kỳ đã đăng ký của môn A hoặc vào các học kỳ tiếp sau. Đ  
  cited: qc-dao-tao · Điều 4 khoản 6
- `q001` **generation** (api: incorrect, local: partial) — 1 tín chỉ thì tương đương bao nhiêu giờ học vậy?  
  expected: 50 giờ học tập (gồm giờ lên lớp, tự học và kiểm tra đánh giá).  
  got: Một tín chỉ tương đương 50 giờ học tập định mức [2]. Tuy nhiên, trong thời gian dự giờ giảng trên lớp, quy đổi cụ thể như sau: một giờ trên lớp được tính là 50 phút (tương đương 1/3 của một tín chỉ) [1]; hoặc đối với hoạt động dạy học trên lớp, một t  
  cited: qc-dao-tao · Điều 4 khoản 1, 2, 3, qd-cong-nhan-tin-chi · Điều 2 khoản 1, 2, 3
- `q006` **generation** (api: partial, local: partial) — Muốn học vượt thì học kỳ chính được đăng ký tối đa bao nhiêu?  
  expected: Không vượt quá 3/2 khối lượng trung bình một học kỳ theo kế hoạch học tập chuẩn.  
  got: Để học vượt, sinh viên có thể đăng ký tối đa **18 tín chỉ** trong các **học kỳ phụ** (bao gồm học kỳ hè và học kỳ dự thính). Tuy nhiên, quy định này không áp dụng cho các **học kỳ chính**. Chi tiết cụ thể như sau: * Đối với **học kỳ phụ**: Sinh viên   
  cited: qc-dao-tao · Điều 12, qc-dao-tao · Điều 6 khoản 1, 2, 3
- `q007` **generation** (api: incorrect, local: partial) — Ngành 4 năm thì tối đa được học bao lâu trước khi bị buộc thôi học?  
  expected: Thời gian chuẩn 4 năm cộng thêm 6 học kỳ.  
  got: Sinh viên ngành 4 năm có thể được gia hạn thời gian học tối đa thêm 6 học kỳ so với kế hoạch chuẩn, tức là tổng thời gian tối đa hoàn thành chương trình là 10 học kỳ (4 học kỳ chuẩn + 6 học kỳ gia hạn) [1]. Tuy nhiên, nếu sinh viên vi phạm quy chế th  
  cited: qc-dao-tao · Điều 5, qc-dao-tao · Điều 17 khoản 2, 3, 4, qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8, phu-luc-vi-pham · (không có mục)
- `q008` **generation** (api: partial, local: partial) — Khóa 5 năm được kéo dài thêm tối đa mấy học kỳ?  
  expected: Thêm 8 học kỳ so với thời gian chuẩn toàn khóa.  
  got: Khóa 5 năm có thể được gia hạn tối đa **8 học kỳ** (tương đương 2 lần gia hạn so với thời gian chuẩn). Cụ thể, quy định như sau: * Thời gian chuẩn để hoàn thành khóa học 5 năm là 10 học kỳ [1]. * Sinh viên có quyền được gia hạn thời hạn tối đa không   
  cited: qc-dao-tao · Điều 5
- `q010` **generation** (api: partial, local: correct) — Hạn chót rút môn là tuần mấy? Rút có được trả lại học phí không?  
  expected: Chậm nhất tuần thứ 7 của học kỳ chính, tuần thứ 2 của học kỳ hè; không được hoàn trả học phí.  
  got: Hạn chót để rút môn học là **tuần lễ thứ 7** của học kỳ chính và **tuần lễ thứ 2** của học kỳ hè [1]. Việc rút môn học **không được hoàn trả lại học phí** [1][2][3]. Các điều kiện và hệ quả liên quan: - Sinh viên phải nộp đơn trực tuyến trên Cổng thô  
  cited: qc-dao-tao · Điều 13 khoản 4, 5, 7, qc-dao-tao · Điều 25 khoản 4, qc-dao-tao · Điều 16 khoản 1, 2
- `q012` **generation** (api: incorrect, local: partial) — Điểm thi cuối kỳ chiếm tối thiểu bao nhiêu phần trăm điểm môn?  
  expected: Không dưới 50%.  
  got: Điểm thi cuối kỳ (ĐCK) chiếm tối thiểu 40% tổng điểm môn học. Điều kiện và quy định liên quan có trong văn bản: 1. Tổng điểm môn học được tính bằng công thức: ĐTK = ĐQT + ĐCK, trong đó ĐQT có tỷ trọng 60% và ĐCK có tỷ trọng 40% [1]. 2. Điểm thi cuối   
  cited: qd-tieng-anh-clc · Điều 3, qc-dao-tao · Điều 21 khoản 1, 2, 3
- `q014` **generation** (api: partial, local: partial) — Bao nhiêu điểm thì qua môn?  
  expected: Từ 5,0 (điểm C) trở lên là đạt và được tích lũy.  
  got: Để được xếp loại "Đạt" (tích lũy) qua môn học theo thang điểm 10, sinh viên cần đạt từ **5,0 đến dưới 6,0** đối với các trường hợp không đạt; tuy nhiên, để đảm bảo đủ điều kiện tốt nghiệp và tránh bị hạ bậc xếp loại, mức điểm tối thiểu an toàn là **6  
  cited: qc-dao-tao · Điều 24 khoản 1, qc-dao-tao · Điều 21 khoản 1, 2, 3, qc-dao-tao · Điều 21 khoản 4, 5, tb-ha-bac-tot-nghiep · (không có mục)
- `q020` **generation** (api: partial, local: correct) — Muốn tốt nghiệp loại giỏi thì GPA phải bao nhiêu?  
  expected: ĐTBTL toàn khóa từ 8,00 đến cận 9,00.  
  got: Để tốt nghiệp loại Giỏi, sinh viên cần có Điểm trung bình tích lũy toàn khóa từ 8,00 đến dưới 9,00 [1]. Ngoài ra, nếu sinh viên thuộc các trường hợp sau, thứ hạng tốt nghiệp sẽ bị giảm đi một mức (từ Giỏi xuống Khá): - Khối lượng môn học phải học lại  
  cited: qc-dao-tao · Điều 31 khoản 5, 6, tb-ha-bac-tot-nghiep · (không có mục), qc-dao-tao · Điều 24 khoản 1
- `q023` **generation** (api: partial, local: correct) — Đi trao đổi ở trường nước ngoài được tích lũy tối đa bao nhiêu tín?  
  expected: Không vượt quá 25% tổng khối lượng của chương trình đào tạo.  
  got: Đi trao đổi ở trường nước ngoài được tích lũy tối đa **25%** tổng khối lượng của Chương trình đào tạo (CTĐT). **Điều kiện và quy định liên quan:** * Sinh viên phải đăng ký thực hiện học một số môn học trao đổi tại cơ sở đào tạo nước ngoài. * Số tín c  
  cited: qc-dao-tao · Điều 19, qc-ren-luyen · Điều 10 khoản 1, qc-ren-luyen · Điều 10 khoản 2, 3, 4
- `q027` **generation** (api: partial, local: correct) — GPA được làm tròn đến mấy chữ số thập phân?  
  expected: 2 chữ số thập phân (điểm môn học làm tròn 1 chữ số).  
  got: GPA (Điểm trung bình tích lũy - ĐTBTL) và điểm trung bình học kỳ (ĐTBHK) được làm tròn đến **2 chữ số thập phân** [2]. Các điều kiện và quy định liên quan: - Công thức tính GPA dựa trên tổng điểm chính thức của các môn học nhân với số tín chỉ chia ch  
  cited: qc-dao-tao · Điều 27
- `q031` **generation** (api: partial, local: partial) — Bị buộc thôi học rồi còn cách nào không?  
  expected: Có thể làm đơn cứu xét trình Hiệu trưởng, hoặc xin chuyển xuống chương trình trình độ thấp hơn/vừa học vừa làm và được bảo lưu một phần kết quả.  
  got: Sau khi bị buộc thôi học, sinh viên có thể thực hiện các hành động sau đây để tiếp tục theo đuổi mục tiêu giáo dục hoặc bảo lưu kết quả học tập của mình: 1. **Làm đơn cứu xét:** Sinh viên có thể nộp đơn xin cứu xét trình Hiệu trưởng xem xét [1]. 2. *  
  cited: qc-dao-tao · Điều 17 khoản 2, 3, 4, qc-dao-tao · Điều 16 khoản 3, 4, qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8
- `q039` **generation** (api: partial, local: correct) — Môn bị điểm R có tính vào GPA không?  
  expected: Không. Điểm R tính chưa tích lũy và không tính vào ĐTBHK, ĐTBTL.  
  got: Môn bị điểm R **không tính vào trung bình điểm học kỳ (ĐTBHK)** và **không tính vào trung bình điểm tổng lớp (ĐTBTL)**, nhưng vẫn được **tính vào tín chỉ tích lũy** [2]. Cụ thể các quy định liên quan như sau: * Các cột điểm của môn học đã được cấp qu  
  cited: qc-dao-tao · Điều 25 khoản 4, qc-dao-tao · Điều 24 khoản 2, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q041` **generation** (api: partial, local: correct) — Điểm học kỳ hè được tính vào học kỳ nào?  
  expected: Tính vào kết quả học tập của học kỳ chính (học kỳ 2).  
  got: Điểm học kỳ hè được tính vào kết quả học tập của **học kỳ chính (học kỳ 2)**. Các điều kiện và hệ quả liên quan có trong văn bản: 1. Kết quả học tập trong học kỳ phụ (hè) được ghi nhận vào điểm bảo lưu, nằm ngoài bảng điểm các học kỳ sinh viên học tạ  
  cited: qc-dao-tao · Điều 26 khoản 1, 2, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, tb-ha-bac-tot-nghiep · (không có mục)
- `q045` **generation** (api: partial, local: correct) — Em rớt một môn tự chọn nhưng đã đủ tín nhóm đó rồi, có xóa điểm đó khỏi GPA được không, nộp đơn lúc nào?  
  expected: Được nộp đơn đề nghị loại bỏ môn không đạt đó khỏi ĐTBTL; nộp ở học kỳ 8 (khóa 4 năm), học kỳ 9 (4,5 năm), học kỳ 10 (5 năm).  
  got: Có, bạn có quyền xóa điểm môn tự chọn chưa đạt khỏi điểm trung bình chung tích lũy (GPA) nếu đã tích lũy đủ số tín chỉ của nhóm môn học tự chọn tương ứng [2]. **Điều kiện và thủ tục liên quan:** * **Điều kiện áp dụng:** Chỉ áp dụng cho môn học thuộc   
  cited: qc-dao-tao · Điều 15, qc-dao-tao · Điều 4 khoản 6
- `q061` **generation** (api: incorrect, local: partial) — Quay cóp trong phòng thi bị kỷ luật mức nào?  
  expected: Theo Nội quy phòng thi: chép bài hoặc cho chép bị trừ 50% điểm thi (mức 2); với môn không dùng tài liệu, bị phát hiện có tài liệu sau khi mở đề thì dù chưa sử dụng cũng bị đình chỉ thi (mức 3). Ngoài   
  got: Quay cóp trong phòng thi sẽ bị xử lý tùy thuộc vào lịch sử vi phạm trước đó của thí sinh theo các mức độ sau: 1. **Mức 1 (Trừ 25% số điểm):** Nếu đây là lần đầu tiên quay cóp, hành vi này được xếp vào lỗi "Chép bài của TS khác hoặc cho TS khác chép b  
  cited: noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh, noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 1. Đối với Cán bộ coi thi, Cán bộ giám sát thi, noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh
- `q063` **over-refusal** (api: correct, local: refused) — Thực tập tốt nghiệp kéo dài bao nhiêu tuần?  
  expected: Tập sự nghề nghiệp kéo dài tối thiểu 02 tháng liên tục, tối đa nguyên 1 học kỳ; tập sự ở nước ngoài theo kế hoạch của Khoa. Văn bản không quy định theo tuần.  
  got: Không tìm thấy trong các văn bản hiện có. Các văn bản cung cấp thông tin về thời hạn tính bằng tháng hoặc học kỳ cho hoạt động tập sự nghề nghiệp (tối thiểu 02 tháng, tối đa 1 học kỳ) [2], [3] và quy trình xét tốt nghiệp [5], nhưng không đề cập đến t  
  cited: qd-tap-su · Điều 5, qd-tap-su · Điều 2, qc-dao-tao · Điều 31 khoản 3, 4
- `q069` **generation** (api: incorrect, local: partial) — Học phần tập sự nghề nghiệp đã học ở trường khác có được công nhận để miễn không?  
  expected: Không. Các học phần tốt nghiệp/khóa luận, tập sự nghề nghiệp và một số học phần ngành do Hội đồng Khoa xác định không được công nhận để miễn học phần (ngoại lệ do Hiệu trưởng phê duyệt).  
  got: Học phần tập sự nghề nghiệp đã học ở trường khác **có thể** được xét công nhận để miễn, nhưng phải đáp ứng các điều kiện và hạn chế cụ thể sau đây: 1. **Đối tượng áp dụng:** Quy định này chỉ áp dụng cho người học đại học tại Trường thuộc đối tượng đã  
  cited: qd-cong-nhan-tin-chi · Điều 3, qd-cong-nhan-tin-chi · Điều 6 khoản 1, qd-cong-nhan-tin-chi · Điều 6 khoản 3, qd-cong-nhan-tin-chi · Điều 6 khoản 1, 2, qd-tap-su · Điều 2
- `q082` **generation** (api: partial, local: correct) — GPA học kỳ 8,2 và điểm rèn luyện 85 thì được thư khen của ai?  
  expected: Thư khen (điện tử) từ Thầy Hiệu trưởng, gửi qua email.  
  got: Sinh viên đạt thành tích học tập Giỏi (GPA ≥ 8,00) và điểm rèn luyện từ 80 điểm trở lên sẽ nhận được **Thư khen do Thầy Hiệu trưởng khen tặng** [1]. Tuy nhiên, để sinh viên năm thứ 2 trở lên (bao gồm năm cuối) có đủ điều kiện xét thư khen của Hiệu tr  
  cited: dk-thu-khen · (không có mục), dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:, dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:
- `q087` **generation** (api: partial, local: correct) — Từ năm 2, mỗi học kỳ phải đạt ít nhất bao nhiêu tín chỉ mới được xét học bổng khuyến khích?  
  expected: Từ 15 tín chỉ trở lên hoặc từ số tín chỉ chuẩn của lộ trình đào tạo học kỳ xét.  
  got: Để từ năm thứ 2 trở lên được xét cấp học bổng khuyến khích học tập trong một học kỳ chính (học kỳ 1 và 2), sinh viên phải đáp ứng các điều kiện về số tín chỉ như sau: * **Số tín chỉ tích lũy:** Phải lớn hơn hoặc bằng số tín chỉ điều kiện, được xác đị  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, qc-dao-tao · Điều 12, dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:
- `q091` **generation** (api: partial, local: partial) — Nữ sinh học ngành Kỹ thuật điện có học bổng riêng không?  
  expected: Có: 10% học phí học kỳ 1 năm học 2025 - 2026 theo khung chương trình tiêu chuẩn.  
  got: Có, nữ sinh viên trúng tuyển và nhập học đợt tuyển sinh năm 2025 vào ngành Kỹ thuật điện được xét cấp Học bổng khuyến khích cho nữ sinh viên với mức tối đa là 10% học phí theo khung chương trình đào tạo tiêu chuẩn học kỳ 1, năm học 2025 - 2026 [1]. N  
  cited: hd-hoc-bong · IV. HỌC BỔNG KHÁC > 6. Học bổng khuyến khích cho nữ sinh viên học ngành kỹ thuật, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 6. Học bổng dành cho ngành có chính sách thu hút
- `q093` **generation** (api: partial, local: correct) — Học lực Giỏi, rèn luyện Tốt thì được hỗ trợ chênh lệch học phí bao nhiêu phần trăm?  
  expected: 70%.  
  got: Học lực Giỏi, rèn luyện Tốt được hỗ trợ chênh lệch học phí **70%** [1]. **Điều kiện và quy định liên quan:** * Để được hỗ trợ, sinh viên phải không vi phạm pháp luật, nội quy nhà trường; đạt kết quả học tập từ 6.0 điểm trở lên; đạt kết quả rèn luyện   
  cited: hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 3. Mức hỗ trợ phần chênh lệch học phí:, hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 4. Lưu ý:, hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 2. Điều kiện:
- `q097` **generation** (api: partial, local: partial) — Học tiếng Anh được nửa kỳ thì em có IELTS, nộp bây giờ có được miễn không?  
  expected: Được miễn học phần đang học (trường hợp 2) nếu nộp trước khi kết thúc môn, nhưng phải làm đơn rút môn (không hoàn học phí) và nhận điểm R; không làm đơn thì vẫn phải học và thi.  
  got: Đáp án: Không thể xác định kết quả miễn học dựa trên câu hỏi của bạn vì thiếu thông tin về thời điểm nộp chứng chỉ so với thời hạn quy định và danh sách học phần cụ thể. **Giải thích:** 1. **Điều kiện thời gian nộp chứng chỉ:** Để được xét miễn, sinh  
  cited: qd-tieng-anh-clc · Điều 4 khoản 2, 3, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ
- `q098` **generation** (api: partial, local: partial) — Phải làm được bao nhiêu phần trăm bài tập mới được thi cuối kỳ tiếng Anh?  
  expected: Ít nhất 80% khối lượng bài tập được giao và đảm bảo chuyên cần.  
  got: Để đủ điều kiện tham gia bài thi đánh giá cuối kỳ (ĐCK) môn tiếng Anh, sinh viên phải hoàn thành ít nhất **80%** khối lượng bài tập được giao và đảm bảo chuyên cần theo đúng yêu cầu của môn học [1]. Ngoài ra, đối với các học phần tiếng Anh cụ thể tro  
  cited: qd-tieng-anh-clc · Điều 3, qd-tieng-anh-clc · PHỤ LỤC 3. HÌNH THỨC ĐÁNH GIÁ VÀ ĐIỀU KIỆN XÉT ĐẠT HỌC PHẦN TIẾNG ANH
- `q102` **generation** (api: incorrect, local: partial) — Giảng viên yêu cầu mở camera khi học online thì có bắt buộc không?  
  expected: Có, người học phải mở camera theo yêu cầu của giảng viên.  
  got: Đáp án: Không bắt buộc theo quy định hiện tại, nhưng giảng viên có quyền yêu cầu người học mở camera để thực hiện tương tác trực tuyến. Giải thích: - Quy định chỉ nêu việc "mở camera theo yêu cầu của giảng viên" chứ không ghi rõ là bắt buộc đối với t  
  cited: qd-ung-dung-cong-nghe · Điều 13 khoản 1, qd-ung-dung-cong-nghe · Điều 13 khoản 2, qd-ung-dung-cong-nghe · Điều 4 khoản 5
- `q103` **generation** (api: partial, local: correct) — Trong tuần sinh hoạt công dân, nội quy quy chế được triển khai qua kênh nào?  
  expected: Qua Hệ thống quản lý học tập (HTQLHT).  
  got: Trong tuần sinh hoạt công dân (SHCD), nội quy, quy chế và quy định được triển khai cho sinh viên thông qua Hệ thống Quản lý Hoạt động Học tập (HTQLHT) [1].  
  cited: qd-ung-dung-cong-nghe · Điều 11
- `q109` **generation** (api: incorrect, local: partial) — Mang đồ ăn vào thư viện lần đầu bị xử lý thế nào?  
  expected: Phê bình (lần 1); lần 7 bị buộc thôi học.  
  got: Mang đồ ăn vào thư viện lần đầu sẽ bị **Nghiêm khắc phê bình**. Theo quy định tại Phụ lục Quy chế công tác sinh viên, hành vi "Mang đồ ăn, thức uống vào phòng học, thư viện" khi vi phạm lần 1 (tính trong cả khóa học) có hình thức xử lý là mức (3) Ngh  
  cited: phu-luc-vi-pham · (không có mục)
- `q123` **hallucination**  — Chương trình tiêu chuẩn cần chuẩn đầu ra tiếng Anh IELTS mấy chấm?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Chương trình tiêu chuẩn cần chuẩn đầu ra tiếng Anh IELTS từ 5.5 điểm trở lên (tất cả các kỹ năng đạt tối thiểu 4.5). Điều kiện này được quy định cụ thể trong Bảng "Chuẩn đầu ra tiếng Anh" cho sinh viên đại học chuyên sâu đặc thù chương trình chất lượ  
  cited: qd-tieng-anh-clc · PHỤ LỤC 4. CHUẨN ĐẦU RA TIẾNG ANH
- `q124` **hallucination**  — Điểm rèn luyện bao nhiêu thì được xét kết nạp Đảng?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Để được xét kết nạp Đảng, sinh viên cần đạt điều kiện về điểm trung bình toàn khóa (≥ 50 điểm) và có kết quả đánh giá rèn luyện được ghi nhận trong cơ sở dữ liệu quản lý người học của Trường [1][4]. Kết quả đánh giá rèn luyện là một trong các tiêu ch  
  cited: qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4, qc-ren-luyen · Điều 8

Causes: generation 27, hallucination 6, over-refusal 1

