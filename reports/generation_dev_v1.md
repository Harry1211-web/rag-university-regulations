# Generation — dev split

62 questions: 57 must be answered, 5 must be refused. Retrieval for RAG is frozen (docs/retrieval.md): top 5 chunks.

| Config | Overall | Multiple choice | Free text (judge) | False refusal | Refusal recall |
|---|---:|---:|---:|---:|---:|
| closed-api | 41% | 80% | 31% | 30% | 60% |
| rag-api | 76% | 60% | 77% | 7% | 100% |
| closed-local | 21% | 70% | 13% | 7% | 0% |
| rag-local | 63% | 70% | 62% | 0% | 60% |

- **Overall**: mean score over all questions (answerable: correct = 1, partial = 0.5; must-refuse: 1 if refused).
- **Free text**: graded by the API judge (the local judge where the API one is missing).
- **False refusal**: answerable questions the model declined. **Refusal recall**: must-refuse questions it declined.

## Citations and grounding (RAG)

| Config | Evidence in context | Cites something | Cites gold chunk | Citation precision | Invalid cite numbers | Grounded (judge) |
|---|---:|---:|---:|---:|---:|---:|
| rag-api | 96% | 100% | 100% | 91% | 0 | 100% |
| rag-local | 96% | 100% | 95% | 67% | 0 | 47% |

## Judge agreement (API judge vs local judge, same answers)

| Config | n | Same label | Cohen's kappa |
|---|---:|---:|---:|
| closed-api | 47 | 83% | 0.77 |
| rag-api | 47 | 53% | 0.03 |
| closed-local | 47 | 68% | 0.52 |
| rag-local | 47 | 60% | 0.32 |

## Errors of rag-api: 26

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd09` **over-refusal**  — Trong kỳ thi tập trung của trường, sinh viên cần làm gì nếu bị trùng lịch thi?  
  expected: Sinh viên kiểm tra lịch thi tổng hợp, nếu các môn học bị trùng lịch thi có lịch thi khác và không trùng với lịch thi của sinh viên, sinh viên nộp đơn Chuyển giờ thi. Nếu các môn học bị trùng lịch khôn  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd11` **over-refusal (evidence missing)**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd17` **over-refusal**  — Sinh viên xem thông báo đóng học phí ở đâu?  
  expected: (see options: None)  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd28` **over-refusal (evidence missing)**  — Khi nào bạn nên tìm đến Chuyên viên Tâm lý của TDTU?  
  expected: Khi cảm thấy áp lực, lo âu, khó thích nghi, gặp biến cố hoặc đơn giản muốn có người lắng nghe.  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `q016` **generation** (api: partial, local: correct) — 6,9 điểm là C+ hay B?  
  expected: C+ (2.5 hệ 4), vì B bắt đầu từ 7,0.  
  got: 6,9 điểm là **C+** (từ 6,0 đến dưới 7,0). [1]  
  cited: qc-dao-tao · Điều 24 khoản 1
- `q022` **generation** (api: partial, local: correct) — Học lại nhiều thì có bị hạ loại bằng không?  
  expected: Có, với loại giỏi và xuất sắc: bị giảm một mức nếu khối lượng môn phải học lại vượt quá 5% tổng số tín chỉ của chương trình (hoặc bị kỷ luật từ mức cảnh cáo trở lên).  
  got: Có, nếu tổng số tín chỉ của các môn phải học lại vượt quá 5% tổng số tín chỉ của chương trình thì sinh viên xếp loại Giỏi hoặc Xuất sắc bị hạ một mức: Giỏi xuống Khá, Xuất sắc xuống Giỏi. [2][3]  
  cited: tb-ha-bac-tot-nghiep · (không có mục), qc-dao-tao · Điều 31 khoản 5, 6
- `q034` **generation** (api: partial, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết là môn phải được sinh viên đăng ký học **và đạt** trước khi đăng ký môn tiếp theo [1]. Văn bản hiện có không nêu định nghĩa cụ thể của môn học trước, nên chưa đủ căn cứ để xác định điểm khác nhau [1][2].  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5
- `q035` **generation** (api: partial, local: correct) — Chưa đóng học phí thì có được thi không?  
  expected: Không. Nợ học phí của học kỳ hiện tại thì không đủ điều kiện dự thi tất cả các môn học trong học kỳ đó và bị ghi điểm F.  
  got: Không. Sinh viên chưa hoàn thành nghĩa vụ học phí đúng thời hạn và không được xét gia hạn sẽ không đủ điều kiện dự thi tất cả các môn học [1].  
  cited: qc-dao-tao · Điều 35
- `q036` **generation** (api: partial, local: correct) — Rớt một môn tự chọn có bắt buộc phải học lại không?  
  expected: Không bắt buộc nếu đã tích lũy đủ số tín chỉ của nhóm tự chọn; có thể học lại môn đó hoặc chọn môn tự chọn khác cùng nhóm.  
  got: Không bắt buộc. Nếu rớt môn tự chọn, sinh viên có thể học lại môn đó hoặc chọn môn tự chọn khác theo quy định; miễn tích lũy đủ số tín chỉ của nhóm tự chọn thì không nhất thiết phải học lại môn đã rớt. [1][2][3]  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 3 khoản 1, 2, qc-dao-tao · Điều 15
- `q037` **generation** (api: partial, local: correct) — Học cải thiện điểm thì có được tính xét học bổng không?  
  expected: Không. Điểm cải thiện không được tính khi xét học bổng khuyến khích học tập và khen thưởng.  
  got: Không. Điểm học cải thiện không được tính khi xét học bổng khuyến khích học tập. [1][2][3]  
  cited: qc-dao-tao · Điều 15, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q040` **generation** (api: partial, local: partial) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Điểm V (vắng thi không phép) được tính như điểm 0. [4]  
  cited: qc-dao-tao · Điều 24 khoản 2
- `q047` **generation** (api: partial, local: correct) — Rút môn thì làm ở đâu?  
  expected: Nộp đơn trực tuyến trên Cổng thông tin sinh viên; môn rút nhận điểm R.  
  got: Sinh viên nộp đơn rút môn học trực tuyến trên Cổng thông tin sinh viên. [1]  
  cited: qc-dao-tao · Điều 13 khoản 4, 5, 7
- `q048` **generation** (api: partial, local: correct) — Muốn phúc khảo bài thi thì làm sao?  
  expected: Nộp đơn phúc khảo trực tuyến trên Cổng thông tin sinh viên; sau khi có kết quả phúc khảo có thể nộp đơn xem lại bài thi cũng trên Cổng.  
  got: Sinh viên nộp đơn phúc khảo trực tuyến trên Cổng thông tin sinh viên. Quy trình thực hiện theo quy định về Khảo thí và đo lường kết quả học tập và Thủ tục phúc khảo bài thi của Trường. [1]  
  cited: qc-dao-tao · Điều 29
- `q049` **generation** (api: partial, local: correct) — Đăng ký học ngành 2 nộp đơn ở đâu?  
  expected: Nộp đơn trực tuyến trên Cổng thông tin sinh viên theo thông báo của Phòng Đại học; Phòng Đại học tổng hợp trình Hiệu trưởng quyết định.  
  got: Sinh viên nộp đơn trực tuyến trên Cổng thông tin sinh viên theo thông báo của Phòng Đại học. [1]  
  cited: qc-dao-tao · Điều 20 khoản 3, 4, 5, 6
- `q055` **generation** (api: partial, local: partial) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh cần IELTS từ 5.5 trở lên, với từng kỹ năng đạt tối thiểu 4.5. [1]  
  cited: qd-tieng-anh-clc · PHỤ LỤC 4. CHUẨN ĐẦU RA TIẾNG ANH
- `q056` **generation** (api: partial, local: partial) — Học bổng khuyến khích cần GPA bao nhiêu?  
  expected: Điểm trung bình tích lũy các môn ngành chính (điểm thi lần 1, không tính môn cải thiện) trong kỳ/năm xét từ loại Khá (7.0) trở lên; kèm điểm rèn luyện từ 65, không có môn dưới 5.0, không thi lại lần 2  
  got: GPA từ **7,0 trở lên (loại Khá)**. Sinh viên năm nhất được xét theo năm học; sinh viên từ năm thứ hai trở lên theo học kỳ xét học bổng. [2][1]  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q058` **generation** (api: partial, local: correct) — Đăng ký ký túc xá thế nào?  
  expected: Liên hệ Ký túc xá (tòa nhà K, ĐT (028) 37 760 652, ktx@tdtu.edu.vn), nơi tiếp nhận thủ tục đăng ký nội trú. Các bước đăng ký cụ thể không có trong các văn bản hiện có.  
  got: Ký túc xá tiếp nhận và giải quyết thủ tục đăng ký nội trú. Bạn có thể liên hệ tại Tòa nhà K, qua số (028) 37 760 652 hoặc email ktx@tdtu.edu.vn. [1]  
  cited: phong-ban · 14. Ký túc xá
- `q064` **generation** (api: partial, local: correct) — Điểm rèn luyện được chấm theo mấy nội dung, mỗi nội dung tối đa bao nhiêu điểm?  
  expected: 6 nội dung (học tập và học thuật; chấp hành nội quy; hoạt động chính trị - xã hội, văn hóa, thể thao; hoạt động cộng đồng, tình nguyện; tinh thần tiên phong, gương mẫu; điểm thưởng), mỗi nội dung tối   
  got: Điểm rèn luyện được chấm theo **6 nội dung**, mỗi nội dung tối đa **20 điểm**. [1]  
  cited: qc-ren-luyen · Điều 3
- `q067` **generation** (api: partial, local: correct) — Bị xếp loại rèn luyện yếu hai học kỳ liên tiếp thì sao?  
  expected: Phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo; nếu bị yếu, kém hai học kỳ liên tiếp lần thứ hai thì bị buộc thôi học (ngoại lệ do Hội đồng quyết định).  
  got: Sinh viên bị xếp loại rèn luyện yếu hai học kỳ liên tiếp phải tạm ngừng học ít nhất một học kỳ tiếp theo. [1]  
  cited: qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8
- `q077` **generation** (api: partial, local: correct) — Tốt nghiệp trễ tiến độ thì có được xét Cử nhân ưu tú không?  
  expected: Không. Chỉ xét sinh viên tốt nghiệp đúng tiến độ hoặc vượt tiến độ, ở ngành học chính.  
  got: Không. Điều kiện xét yêu cầu sinh viên tốt nghiệp đúng hoặc vượt tiến độ; quy định chung cũng nêu sinh viên phải tốt nghiệp đúng hoặc trước tiến độ. [1][2]  
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú, qd-cu-nhan-uu-tu · I. Quy định chung
- `q078` **generation** (api: partial, local: partial) — Không học Ngôn ngữ Anh thì cần IELTS bao nhiêu để được Cử nhân ưu tú?  
  expected: IELTS ≥ 5.5 (hoặc PET/FCE ≥ 160, TOEFL iBT ≥ 50; TOEIC Nghe & Đọc ≥ 600).  
  got: Các ngành khác cần IELTS ≥ 5.5; riêng ngành Ngôn ngữ Trung Quốc (chuyên ngành Trung – Anh) cần IELTS ≥ 6.0 để đạt điều kiện tiếng Anh xét Cử nhân/Kỹ sư ưu tú. [1]  
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú
- `q084` **generation** (api: partial, local: correct) — Có môn bị điểm R thì còn được xét thư khen không?  
  expected: Vẫn được tham gia xét thư khen (áp dụng cả điểm H, P).  
  got: Có. Sinh viên có môn chưa đạt do rút môn học (điểm R) vẫn được tham gia xét thư khen [1][2].  
  cited: dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:, dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:
- `q094` **generation** (api: partial, local: correct) — Em là người đầu tiên trong nhà học đại học thì có học bổng không?  
  expected: Có nếu trúng tuyển vào ngành thuộc nhóm thu hút 1, có đơn và xác nhận của địa phương: 20% học phí học kỳ 1 năm học 2025 - 2026; được xét tiếp các học kỳ sau nếu học tập, rèn luyện từ Khá và không bị k  
  got: Có. Nếu em trúng tuyển và nhập học vào nhóm ngành thu hút 1, đồng thời nộp đơn đề nghị và có xác nhận của địa phương theo mẫu TDTU, em được xét học bổng 20% học phí học kỳ 1 năm học 2025–2026. [1]  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học
- `q108` **generation** (api: partial, local: partial) — Được dùng bút chì để làm bài thi không?  
  expected: Không, chỉ làm bài bằng 01 màu mực; bút chì chỉ dùng để vẽ hình hoặc dùng compa; không dùng bút đỏ, bút xóa.  
  got: Chỉ được dùng bút chì để vẽ hình hoặc sử dụng compa; các trường hợp khác không được dùng bút chì làm bài thi. [1]  
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh
- `q113` **generation** (api: partial, local: correct) — Bị trừ 25% điểm thi lần đầu thì có bị kỷ luật thêm không?  
  expected: Có: nghiêm khắc phê bình (lần 1), khiển trách (lần 2), ... đến buộc thôi học (lần 6).  
  got: Có. Nếu vi phạm lần đầu bị xử lý ở mức trừ 25% điểm thi, hình thức xử lý tương ứng là **nghiêm khắc phê bình**; số lần vi phạm được tính trong cả khóa học. [1]  
  cited: phu-luc-vi-pham · (không có mục)
- `q119` **generation** (api: partial, local: correct) — Thư viện trường nằm ở đâu?  
  expected: Tòa nhà Thư viện truyền cảm hứng (tòa nhà G); ĐT (028) 37755057, thuvien@tdtu.edu.vn.  
  got: Thư viện nằm tại Tòa nhà Thư viện truyền cảm hứng (Tòa nhà G). [1]  
  cited: phong-ban · 9. Thư viện; 10. Viện hợp tác, nghiên cứu và đào tạo quốc tế

Causes: generation 22, over-refusal 2, over-refusal (evidence missing) 2

## Errors of rag-local: 34

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd05` **hallucination**  — Sơ đồ đào tạo và sơ đồ tích lũy có giống nhau không?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b **Giải thích:** Các văn bản hiện có quy định về cấu trúc chương trình đào tạo, phương thức tính điểm trung bình (điểm học kỳ, điểm tích lũy) và các điều kiện ràng buộc môn học nhưng **không chứa thông tin cụ thể** về giao diện hiển thị của   
  cited: —
- `shcd11` **retrieval**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Đáp án: c Giải thích: Theo quy định tính điểm môn học trong các văn bản hiện có, điểm môn học được tính bằng tổng cộng các thành phần (Quá trình, Giữa kỳ, Cuối kỳ) nhân với tỷ trọng tương ứng của từng thành phần đó. Tuy nhiên, các đoạn trích [1], [2]  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, qc-ren-luyen · Điều 4, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế
- `shcd17` **generation**  — Sinh viên xem thông báo đóng học phí ở đâu?  
  expected: (see options: None)  
  got: Đáp án: a **Giải thích:** Theo quy định trong văn bản [1], Phòng Tài chính có trách nhiệm thông báo học phí, thời gian nộp và hướng dẫn cách thức nộp cho sinh viên. Tuy nhiên, các đoạn trích hiện có **không nêu rõ** địa điểm cụ thể (như Cổng thông ti  
  cited: qc-dao-tao · Điều 35, phong-ban · 8. Phòng Tài chính, qc-dao-tao · Điều 30
- `shcd25` **generation**  — Sinh viên bị điểm “F” (không đủ điều kiện thi) khi:  
  expected: Tất cả các đáp án trên đều đúng  
  got: Đáp án: a Giải thích: - Theo Điều 25, khoản 1, mục d) trong văn bản [1], sinh viên bị điểm "F" khi không hoàn thành nghĩa vụ học phí theo quy định. - Tuy nhiên, đối với các lựa chọn b và c, văn bản hiện có chưa cung cấp thông tin cụ thể để khẳng định  
  cited: qc-dao-tao · Điều 25 khoản 1, qd-tieng-anh-clc · Điều 3, qc-dao-tao · Điều 24 khoản 2
- `shcd26` **hallucination**  — Nguyên tắc ứng xử của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b Giải thích: Theo đoạn trích [1], mục tiêu của Bộ Quy tắc ứng xử là tạo lập môi trường học tập "bình đẳng, công bằng, văn minh và hiệu quả". Tuy nhiên, trong các lựa chọn đã cho, chỉ có đáp án **b** ("Giáo dục, nghiên cứu và sáng tạo vì sự p  
  cited: quy-tac-ung-xu · I. MỤC TIÊU VÀ NGUYÊN TẮC:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 1. TẠO LẬP MÔI TRƯỜNG VĂN MINH VÀ CÓ CHUẨN MỰC:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 7. TÔN TRỌNG QUYỀN SỞ HỮU TRÍ TUỆ:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 6. ỨNG XỬ TRONG HỌC THUẬT:
- `q003` **generation** (api: partial, local: correct) — Học kỳ chính phải đăng ký ít nhất bao nhiêu tín chỉ?  
  expected: 10 tín chỉ, trừ học kỳ cuối khóa và sinh viên chưa đạt trình độ tiếng Anh theo quy định.  
  got: Học kỳ chính phải đăng ký ít nhất **10 tín chỉ**. Tuy nhiên, quy định có một ngoại lệ đối với sinh viên không đạt trình độ tiếng Anh được quy định tại Điều 12 khoản 1 điểm b: họ sẽ bị hạn chế số tín chỉ đăng ký hoặc ngừng học các môn khác (ngoại trừ   
  cited: qc-dao-tao · Điều 12
- `q016` **generation** (api: incorrect, local: incorrect) — 6,9 điểm là C+ hay B?  
  expected: C+ (2.5 hệ 4), vì B bắt đầu từ 7,0.  
  got: Đáp án: Không có lựa chọn cụ thể trong văn bản hiện có. Giải thích: - Theo Bảng 1 trong [1], điểm từ 7,0 đến cận 8,0 được xếp loại "Khá" (điểm chữ tham khảo B), còn điểm từ 6,0 đến cận 7,0 được xếp loại "Trung bình khá" (điểm chữ tham khảo C+). - Điể  
  cited: qc-dao-tao · Điều 24 khoản 1
- `q017` **generation** (api: incorrect, local: partial) — Bị điểm H thi cuối kỳ thì có bao lâu để thi lại?  
  expected: Trong 01 năm học kế tiếp; quá hạn điểm H chuyển thành điểm 0.  
  got: Đáp án: Không tìm thấy trong các văn bản hiện có. **Giải thích:** Các đoạn trích cung cấp thông tin về thời hạn để thi lại đối với sinh viên bị điểm H của **điểm kiểm tra tập trung giữa kỳ** (trong cùng học kỳ) [1] và **điểm kiểm tra cuối kỳ của học   
  cited: qc-dao-tao · Điều 25 khoản 2
- `q022` **generation** (api: partial, local: correct) — Học lại nhiều thì có bị hạ loại bằng không?  
  expected: Có, với loại giỏi và xuất sắc: bị giảm một mức nếu khối lượng môn phải học lại vượt quá 5% tổng số tín chỉ của chương trình (hoặc bị kỷ luật từ mức cảnh cáo trở lên).  
  got: Có, việc học lại nhiều sẽ dẫn đến hạ bậc xếp loại tốt nghiệp nếu khối lượng môn học phải học lại vượt quá 5% tổng số tín chỉ quy định cho toàn chương trình [1][3]. Tuy nhiên, mức độ hạ bậc cụ thể (từ Giỏi xuống Khá hay từ Xuất sắc xuống Giỏi) phụ thu  
  cited: tb-ha-bac-tot-nghiep · (không có mục), qc-dao-tao · Điều 31 khoản 5, 6, qc-dao-tao · Điều 4 khoản 6
- `q034` **generation** (api: incorrect, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết và môn học trước khác nhau ở điều kiện bắt buộc để đăng ký học và cách thức áp dụng như sau: 1. **Về điều kiện bắt buộc:** * **Môn tiên quyết:** Điều kiện bắt buộc để đăng ký học môn B là sinh viên đã đăng ký học và đạt môn A (theo tha  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5, qc-dao-tao · Điều 13 khoản 1, 2, qc-dao-tao · Điều 25 khoản 5, 6
- `q035` **generation** (api: partial, local: correct) — Chưa đóng học phí thì có được thi không?  
  expected: Không. Nợ học phí của học kỳ hiện tại thì không đủ điều kiện dự thi tất cả các môn học trong học kỳ đó và bị ghi điểm F.  
  got: Không, sinh viên chưa đóng học phí thì không đủ điều kiện dự thi. Theo quy định, sinh viên thực hiện nghĩa vụ nộp học phí trong thời gian Trường thông báo để đảm bảo các quyền lợi học và thi [1]. Nếu sinh viên không hoàn thành nghĩa vụ học phí đúng t  
  cited: qc-dao-tao · Điều 35
- `q037` **generation** (api: partial, local: partial) — Học cải thiện điểm thì có được tính xét học bổng không?  
  expected: Không. Điểm cải thiện không được tính khi xét học bổng khuyến khích học tập và khen thưởng.  
  got: Không tìm thấy trong các văn bản hiện có thông tin chi tiết về việc "học cải thiện" cụ thể có được tính vào xét học bổng hay không, tuy nhiên văn bản ghi rõ nguyên tắc loại trừ các môn học cải thiện. Cụ thể: - Đối với sinh viên năm thứ nhất, điều kiệ  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q040` **generation** (api: partial, local: partial) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Điểm "Vắng thi không phép" (gọi là "điểm V") được ghi nhận cho sinh viên đủ điều kiện dự thi và có tên trong danh sách thi nhưng vắng thi không có lý do chính đáng [1]. Điểm này được tính như điểm 0, không tính vào tín chỉ tích lũy, điểm trung bình h  
  cited: qc-dao-tao · Điều 25 khoản 5, 6, qc-dao-tao · Điều 24 khoản 2
- `q042` **generation** (api: partial, local: partial) — Muốn bảo lưu vì lý do cá nhân thì cần điều kiện gì?  
  expected: Đã học tối thiểu 01 học kỳ, không thuộc diện bị xem xét buộc thôi học hoặc kỷ luật, ĐTBTL không dưới 5,00; thời gian nghỉ vẫn tính vào thời gian học tối đa.  
  got: Để sinh viên được xin nghỉ học tạm thời và bảo lưu kết quả vì lý do cá nhân, cần đáp ứng các điều kiện sau: 1. Sinh viên phải thực hiện nghĩa vụ học phí môn học còn nợ theo quy định của Trường [1]. 2. Phải đạt điểm trung bình chung tích lũy không dướ  
  cited: qc-dao-tao · Điều 16 khoản 3, 4, qc-dao-tao · Điều 16 khoản 1, 2, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 3. Nguyên tắc xét cấp học bổng:, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường, hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 4. Lưu ý:
- `q047` **generation** (api: partial, local: correct) — Rút môn thì làm ở đâu?  
  expected: Nộp đơn trực tuyến trên Cổng thông tin sinh viên; môn rút nhận điểm R.  
  got: Sinh viên nộp đơn xin rút môn học trực tuyến trên Cổng thông tin sinh viên [1].  
  cited: qc-dao-tao · Điều 13 khoản 4, 5, 7
- `q049` **generation** (api: incorrect, local: refused) — Đăng ký học ngành 2 nộp đơn ở đâu?  
  expected: Nộp đơn trực tuyến trên Cổng thông tin sinh viên theo thông báo của Phòng Đại học; Phòng Đại học tổng hợp trình Hiệu trưởng quyết định.  
  got: Đáp án: Không tìm thấy trong các văn bản hiện có. Giải thích: Các đoạn trích [1], [2], [3], [4] và [5] đã đề cập đến việc nộp đơn đăng ký môn học, đăng ký học thêm chương trình thứ hai hoặc đăng ký tập sự nghề nghiệp (trên Cổng thông tin sinh viên ho  
  cited: qc-dao-tao · Điều 20 khoản 3, 4, 5, 6, qc-dao-tao · Điều 20 khoản 7, 8, qc-dao-tao · Điều 13 khoản 4, 5, 7, qc-dao-tao · Điều 20 khoản 1, 2, qd-tap-su · Điều 7
- `q053` **generation** (api: partial, local: correct) — Bị trùng lịch thi hai môn thì xin hoãn thi thế nào?  
  expected: Nộp đơn Hoãn thi trong thời gian quy định được công bố cùng lịch thi để được ghi nhận điểm H.  
  got: Để xin hoãn thi khi bị trùng lịch thi, sinh viên cần thực hiện các bước sau dựa trên văn bản: 1. **Nộp đơn:** Sinh viên phải nộp đơn "Hoãn thi" trong thời gian quy định được công bố cùng lịch thi [1]. 2. **Kèm theo xác nhận:** Đơn Hoãn thi phải kèm t  
  cited: qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 23, qc-dao-tao · Điều 22
- `q055` **generation** (api: partial, local: partial) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh cho sinh viên trình độ đại học, chuyên sâu đặc thù chương trình chất lượng cao yêu cầu IELTS từ **≥ 5.5** (tất cả kỹ năng ≥ 4.5) [1]. Tuy nhiên, nếu xét về điều kiện để được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú, mức yêu cầu   
  cited: qd-tieng-anh-clc · PHỤ LỤC 4. CHUẨN ĐẦU RA TIẾNG ANH, qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ
- `q056` **generation** (api: partial, local: partial) — Học bổng khuyến khích cần GPA bao nhiêu?  
  expected: Điểm trung bình tích lũy các môn ngành chính (điểm thi lần 1, không tính môn cải thiện) trong kỳ/năm xét từ loại Khá (7.0) trở lên; kèm điểm rèn luyện từ 65, không có môn dưới 5.0, không thi lại lần 2  
  got: Đáp án: Không có trong các văn bản hiện có. Giải thích: Các văn bản cung cấp chỉ nêu yêu cầu về "Điểm trung bình tích lũy" phải đạt từ loại **Khá (7.0) trở lên** [1], [2] hoặc điểm rèn luyện từ **65 điểm trở lên** [1], [2]. Tuy nhiên, các văn bản khô  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q057` **generation** (api: partial, local: correct) — Điểm rèn luyện toàn khóa tối thiểu bao nhiêu thì được tốt nghiệp?  
  expected: Điểm rèn luyện trung bình toàn khóa phải từ 50 điểm trở lên.  
  got: Điểm rèn luyện toàn khóa tối thiểu để xét tốt nghiệp là **50 điểm** (tương đương ĐTBTL ≥ 5,00). * Căn cứ theo Điều 15 khoản 4a Quy chế đánh giá kết quả rèn luyện: "Điểm trung bình toàn khóa phải ≥ 50 điểm" [1]. * Căn cứ theo Điều 31 khoản 2 quy định   
  cited: qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4, qc-dao-tao · Điều 31 khoản 5, 6, qc-dao-tao · Điều 31 khoản 1, 2
- `q058` **generation** (api: partial, local: partial) — Đăng ký ký túc xá thế nào?  
  expected: Liên hệ Ký túc xá (tòa nhà K, ĐT (028) 37 760 652, ktx@tdtu.edu.vn), nơi tiếp nhận thủ tục đăng ký nội trú. Các bước đăng ký cụ thể không có trong các văn bản hiện có.  
  got: Để đăng ký ký túc xá, bạn cần liên hệ trực tiếp với phòng ban phụ trách hoặc các đơn vị tổ chức hoạt động tại Ký túc xá. Cụ thể: - Bạn có thể liên hệ để giải quyết thủ tục (như đăng ký nội trú) và được thông tin về bảo hiểm y tế, bảo vệ cũng như ký t  
  cited: phong-ban · 14. Ký túc xá, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 2. Học bổng áp dụng cho con, anh/chị em ruột của cán bộ công đoàn; 3. Học bổng sinh viên nội trú Ký túc xá, phong-ban · 1. Phòng Tổ chức hành chính:, hd-hoc-bong · IX. HỖ TRỢ NGƯỜI HỌC > 2. Hỗ trợ một phần chi phí Ký túc xá tại Phân hiệu Khánh Hòa
- `q064` **generation** (api: partial, local: partial) — Điểm rèn luyện được chấm theo mấy nội dung, mỗi nội dung tối đa bao nhiêu điểm?  
  expected: 6 nội dung (học tập và học thuật; chấp hành nội quy; hoạt động chính trị - xã hội, văn hóa, thể thao; hoạt động cộng đồng, tình nguyện; tinh thần tiên phong, gương mẫu; điểm thưởng), mỗi nội dung tối   
  got: Điểm rèn luyện được chấm theo **7 nội dung**, mỗi nội dung có mức tối đa là **20 điểm**. Các nội dung cụ thể như sau: 1. Việc tham gia học tập và các hoạt động chuyên môn học thuật: tối đa 20 điểm [1]. 2. Việc chấp hành nội quy, quy chế, quy định tro  
  cited: qc-ren-luyen · Điều 3
- `q067` **generation** (api: partial, local: correct) — Bị xếp loại rèn luyện yếu hai học kỳ liên tiếp thì sao?  
  expected: Phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo; nếu bị yếu, kém hai học kỳ liên tiếp lần thứ hai thì bị buộc thôi học (ngoại lệ do Hội đồng quyết định).  
  got: Sinh viên bị buộc thôi học nếu bị xếp loại rèn luyện yếu, kém trong hai học kỳ liên tiếp lần thứ hai. Trường hợp này sinh viên phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo; các trường hợp ngoại lệ do Hội đồng xem xét quyết định [1].  
  cited: qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8
- `q071` **generation** (api: partial, local: partial) — Khối lượng học tập được công nhận và chuyển đổi tín chỉ tối đa là bao nhiêu?  
  expected: Với chương trình đại học: không vượt quá 50% khối lượng học tập của chương trình đào tạo đang học.  
  got: Khối lượng học tập được công nhận và chuyển đổi tín chỉ tối đa phụ thuộc vào trình độ đào tạo đang học, cụ thể như sau: * Đối với chương trình đào tạo đại học (CTĐT đại học): Tối đa không vượt quá **50%** khối lượng học tập của CTĐT đang học [1][2].   
  cited: qc-dao-tao · Điều 28, qd-cong-nhan-tin-chi · Điều 3
- `q078` **generation** (api: partial, local: partial) — Không học Ngôn ngữ Anh thì cần IELTS bao nhiêu để được Cử nhân ưu tú?  
  expected: IELTS ≥ 5.5 (hoặc PET/FCE ≥ 160, TOEFL iBT ≥ 50; TOEIC Nghe & Đọc ≥ 600).  
  got: Để được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú mà không học chương trình Ngôn ngữ Anh, sinh viên thuộc các ngành khác phải đạt yêu cầu năng lực Tiếng Anh như sau: IELTS ≥ 5.5 hoặc PET/FCE ≥ 160 hoặc TOEFL iBT ≥ 50 [1]. Tuy nhiên, văn bản hiện có **k  
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú
- `q086` **generation** (api: incorrect, local: partial) — Học lực Xuất sắc nhưng rèn luyện chỉ Khá thì nhận học bổng loại gì?  
  expected: Học bổng loại Khá.  
  got: Đáp án: Không tìm thấy trong các văn bản hiện có. **Giải thích:** * Văn bản [1] cung cấp bảng quy định cụ thể về việc xét cấp học bổng dựa trên sự kết hợp giữa "Kết quả học tập" và "Kết quả rèn luyện". Tuy nhiên, trong toàn bộ các điều kiện được liệt  
  cited: hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 3. Nguyên tắc xét cấp học bổng:, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 3. Nguyên tắc xét cấp học bổng:, dk-thu-khen · (không có mục), hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q088` **generation** (api: partial, local: partial) — Hai anh em ruột cùng học ở trường thì có học bổng không?  
  expected: Có: 15% học phí theo khung chương trình tiêu chuẩn mỗi năm học, áp dụng từ người thứ hai; cấp vào cuối năm học.  
  got: Có, hai anh em ruột cùng học ở trường sẽ được xét cấp học bổng nếu thỏa mãn điều kiện là đang học ngành chính tại Trường theo đúng khóa học [1]. Tuy nhiên, chỉ **một** trong số họ sẽ được nhận học bổng. Nếu là cặp song sinh, sinh viên phải tự lựa chọ  
  cited: hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường
- `q094` **generation** (api: partial, local: correct) — Em là người đầu tiên trong nhà học đại học thì có học bổng không?  
  expected: Có nếu trúng tuyển vào ngành thuộc nhóm thu hút 1, có đơn và xác nhận của địa phương: 20% học phí học kỳ 1 năm học 2025 - 2026; được xét tiếp các học kỳ sau nếu học tập, rèn luyện từ Khá và không bị k  
  got: Có, nếu bạn thỏa mãn các điều kiện sau: trúng tuyển và nhập học vào nhóm thu hút 1 theo danh mục các ngành học có chính sách thu hút của Hướng dẫn này [1]; có đơn đề nghị xét cấp học bổng và có xác nhận của địa phương theo mẫu của TDTU [1]. Mức học b  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học
- `q099` **generation** (api: partial, local: partial) — Chương trình kỹ sư chất lượng cao có mấy học phần tiếng Anh?  
  expected: 05 học phần tiếng Anh dự bị ngoài chương trình và 05 học phần tiếng Anh chính thức.  
  got: Chương trình kỹ sư chất lượng cao gồm tổng cộng **09** học phần tiếng Anh. Cụ thể bao gồm: - 05 học phần tiếng Anh dự bị tập trung (Tiếng Anh dự bị 1, 2, 3, 4, 5) [3][4]. - 04 học phần tiếng Anh chính thức (Tiếng Anh 1, 2, 3, 4) [2][4]. - 01 học phần  
  cited: qd-tieng-anh-clc · Điều 2 khoản 1, 2, 3, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY, qd-tieng-anh-clc · PHỤ LỤC 1. CHƯƠNG TRÌNH HỌC TIẾNG ANH THEO KẾ HOẠCH GIẢNG DẠY
- `q106` **generation** (api: partial, local: correct) — Làm bài xong thì bao lâu được nộp bài ra về?  
  expected: Sau 1/2 thời gian thi.  
  got: Theo quy định, thời gian nộp bài và ra về phụ thuộc vào hình thức thi cũng như thời điểm trong quá trình thi: 1. **Sau 1/2 thời gian thi:** Thí sinh được phép nộp bài làm cùng giấy thi, giấy nháp, đề thi và ra về [1]. 2. **Khi hết giờ làm bài:** Thí   
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh, noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 1. Cán bộ coi thi
- `q108` **generation** (api: partial, local: partial) — Được dùng bút chì để làm bài thi không?  
  expected: Không, chỉ làm bài bằng 01 màu mực; bút chì chỉ dùng để vẽ hình hoặc dùng compa; không dùng bút đỏ, bút xóa.  
  got: Được phép dùng bút chì trong trường hợp vẽ hình hoặc sử dụng compa [1].  
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh
- `q111` **generation** (api: incorrect, local: partial) — Thi hộ người khác bị xử lý thế nào?  
  expected: Lần 1 đình chỉ học tập có thời hạn, lần 2 buộc thôi học.  
  got: Thi hộ người khác sẽ bị xử lý như sau tùy theo mức độ vi phạm và số lần tái phạm: 1. **Đối với hành vi thi hộ:** * Nếu là lần đầu tiên (tính trong cả khóa học): Bị **buộc thôi học** [2]. * Nếu tổ chức thi hộ cho người khác: Bị **buộc thôi học** ngay   
  cited: phu-luc-vi-pham · (không có mục)
- `q113` **generation** (api: incorrect, local: partial) — Bị trừ 25% điểm thi lần đầu thì có bị kỷ luật thêm không?  
  expected: Có: nghiêm khắc phê bình (lần 1), khiển trách (lần 2), ... đến buộc thôi học (lần 6).  
  got: Đáp án: Không có thông tin cụ thể về việc "bị kỷ luật thêm" khi bị trừ 25% điểm thi lần đầu trong các văn bản hiện có. Các văn bản chỉ quy định mức xử lý dựa trên số lần vi phạm và nội dung cụ thể của hành vi, không nêu rõ trường hợp bị trừ 25% điểm   
  cited: phu-luc-vi-pham · (không có mục), noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh
- `q119` **generation** (api: partial, local: correct) — Thư viện trường nằm ở đâu?  
  expected: Tòa nhà Thư viện truyền cảm hứng (tòa nhà G); ĐT (028) 37755057, thuvien@tdtu.edu.vn.  
  got: Thư viện trường nằm tại Tòa nhà Thư viện truyền cảm hứng (Tòa nhà G). [1]  
  cited: phong-ban · 9. Thư viện; 10. Viện hợp tác, nghiên cứu và đào tạo quốc tế

Causes: generation 31, hallucination 2, retrieval 1

