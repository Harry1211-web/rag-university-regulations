# Generation — dev split

62 questions: 56 must be answered, 6 must be refused. Retrieval for RAG is frozen (docs/retrieval.md): top 5 chunks.

| Config | Overall | Multiple choice | Free text (judge) | False refusal | Refusal recall |
|---|---:|---:|---:|---:|---:|
| closed-api | 44% | 89% | 34% | 30% | 50% |
| rag-api | 91% | 89% | 97% | 2% | 50% |
| closed-local | 22% | 78% | 14% | 7% | 0% |
| rag-local | 72% | 89% | 73% | 0% | 33% |

- **Overall**: mean score over all questions (answerable: correct = 1, partial = 0.5; must-refuse: 1 if refused).
- **Free text**: graded by the API judge (the local judge where the API one is missing).
- **False refusal**: answerable questions the model declined. **Refusal recall**: must-refuse questions it declined.

## Citations and grounding (RAG)

| Config | Evidence in context | Cites something | Cites gold chunk | Citation precision | Invalid cite numbers | Grounded (judge) |
|---|---:|---:|---:|---:|---:|---:|
| rag-api | 96% | 100% | 98% | 85% | 0 | 100% |
| rag-local | 96% | 100% | 95% | 55% | 1 | 47% |

## Judge agreement (API judge vs local judge, same answers)

| Config | n | Same label | Cohen's kappa |
|---|---:|---:|---:|
| closed-api | 47 | 68% | 0.59 |
| rag-api | 47 | 70% | 0.13 |
| closed-local | 47 | 60% | 0.38 |
| rag-local | 47 | 68% | 0.39 |

## Errors of rag-api: 7

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd05` **hallucination**  — Sơ đồ đào tạo và sơ đồ tích lũy có giống nhau không?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b Đoạn trích xác nhận chương trình đào tạo gồm các môn học [1], còn điểm trung bình học kỳ và tích lũy được tính từ các môn đã học [4]. Tuy nhiên, các đoạn trích không mô tả trực tiếp chức năng hay nội dung hiển thị của hai sơ đồ; vì vậy chỉ   
  cited: qc-dao-tao · Điều 2 khoản 1, 2, 3, qc-dao-tao · Điều 27
- `shcd11` **over-refusal (evidence missing)**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Không tìm thấy trong các văn bản hiện có.  
  cited: —
- `shcd17` **hallucination**  — Sinh viên xem thông báo đóng học phí ở đâu?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: a Các đoạn trích cho biết Phòng Tài chính thông báo học phí, thời gian nộp và hướng dẫn cách nộp; tuy nhiên, không nêu cụ thể Cổng thông tin sinh viên hay đường dẫn phân hệ như trong lựa chọn a. [1][2]  
  cited: qc-dao-tao · Điều 35, phong-ban · 8. Phòng Tài chính
- `shcd26` **hallucination**  — Nguyên tắc ứng xử của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: a Đoạn trích nêu mục tiêu tạo lập môi trường học tập, nghiên cứu bình đẳng, công bằng và hiệu quả; đây là lựa chọn được văn bản ủng hộ nhiều nhất. [1]  
  cited: quy-tac-ung-xu · I. MỤC TIÊU VÀ NGUYÊN TẮC:
- `q034` **generation** (api: partial, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết yêu cầu sinh viên **đã đăng ký học và đạt** môn đó thì mới được đăng ký môn học tiếp theo. [1] Các đoạn trích hiện có **chưa nêu định nghĩa hoặc điều kiện cụ thể của môn học trước**, nên chưa đủ căn cứ để xác định đầy đủ điểm khác nhau  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5, qc-dao-tao · Điều 13 khoản 1, 2
- `q040` **generation** (api: partial, local: correct) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Vắng thi không phép nhận điểm V, được tính như điểm 0. Trường hợp này cũng được xem là đã dự thi một lần. [2][4]  
  cited: qc-dao-tao · Điều 23, qc-dao-tao · Điều 24 khoản 2
- `q055` **generation** (api: partial, local: partial) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh yêu cầu IELTS từ **5.5 trở lên**, đồng thời **mỗi kỹ năng đạt ít nhất 4.5**. [1]  
  cited: qd-tieng-anh-clc · PHỤ LỤC 4. CHUẨN ĐẦU RA TIẾNG ANH

Causes: hallucination 3, generation 3, over-refusal (evidence missing) 1

## Errors of rag-local: 27

Cause: **retrieval** = the evidence was not in the 5 chunks; **generation** = it was, but the answer is wrong; **over-refusal** / **hallucination** = refused an answerable question / answered a must-refuse one.

- `shcd05` **hallucination**  — Sơ đồ đào tạo và sơ đồ tích lũy có giống nhau không?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b **Giải thích:** Các văn bản hiện có quy định về cấu trúc chương trình đào tạo (bao gồm khối lượng học tập chung/r riêng, môn bắt buộc/tự chọn, tỷ lệ lý thuyết/thực hành) và các điều kiện ràng buộc như lộ trình tiếng Anh, điều kiện tiên quyế  
  cited: qc-dao-tao · Điều 2 khoản 1, 2, 3, qd-tieng-anh-clc · Điều 5
- `shcd11` **retrieval**  — Sinh viên học môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 có các cột điểm Quá trình 1 (10%): 10 điểm, Quá trình 2 (20%): 8 điểm, Giữa kỳ (20%): 5 điểm, Cuối kỳ (50%): 7 điểm. Điểm môn Toán kinh tế (2 tín chỉ) học kỳ 2/2025-2026 của sinh viên bao nhiêu?  
  expected: 7,1  
  got: Đáp án: c **Giải thích:** Theo quy định trong văn bản, điểm môn học được tính bằng tổng các thành phần nhân với tỷ trọng tương ứng [4]. Tuy nhiên, các đoạn trích văn bản hiện có **không nêu công thức cụ thể để tính điểm trung bình của một môn học dựa  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 8. Học bổng chương trình liên kết đào tạo quốc tế
- `shcd17` **hallucination**  — Sinh viên xem thông báo đóng học phí ở đâu?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: a Theo quy định tại Điều 35, Khoản 1 trong văn bản [1], Phòng Tài chính có trách nhiệm thông báo học phí cho sinh viên về thời gian nộp và cách thức nộp. Tuy nhiên, các đoạn trích hiện có không nêu rõ vị trí cụ thể trên Cổng thông tin sinh vi  
  cited: qc-dao-tao · Điều 35, phong-ban · 8. Phòng Tài chính, qc-dao-tao · Điều 30
- `shcd26` **hallucination**  — Nguyên tắc ứng xử của Trường Đại học Tôn Đức Thắng  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Đáp án: b Giải thích: Theo đoạn trích [1], mục tiêu của Bộ Quy tắc ứng xử là tạo lập môi trường học tập "bình đẳng, công bằng, văn minh và hiệu quả". Tuy nhiên, khi xem xét các lựa chọn trong đề bài, chỉ có lựa chọn **b** ("Giáo dục, nghiên cứu và sá  
  cited: quy-tac-ung-xu · I. MỤC TIÊU VÀ NGUYÊN TẮC:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 7. TÔN TRỌNG QUYỀN SỞ HỮU TRÍ TUỆ:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 4. TỰ DO THỂ HIỆN QUAN ĐIỂM CÁ NHÂN TRONG KHUÔN KHỔ PHÁP LUẬT:, quy-tac-ung-xu · II. NỘI DUNG CỦA QUY TẮC: > 6. ỨNG XỬ TRONG HỌC THUẬT:
- `q003` **generation** (api: partial, local: partial) — Học kỳ chính phải đăng ký ít nhất bao nhiêu tín chỉ?  
  expected: 10 tín chỉ, trừ học kỳ cuối khóa và sinh viên chưa đạt trình độ tiếng Anh theo quy định.  
  got: Học kỳ chính phải đăng ký ít nhất **10 tín chỉ**. Tuy nhiên, mức tối thiểu này có các ngoại lệ và điều kiện cụ thể như sau: * **Trường hợp trừ:** Quy định 10 tín chỉ không áp dụng đối với sinh viên ở các học kỳ phụ (học kỳ hè, học kỳ dự thính) [1]. *  
  cited: qc-dao-tao · Điều 12, dk-thu-khen · 1. Sinh viên được nhận thư khen thỏa các điều kiện:, qc-dao-tao · Điều 17 khoản 1, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:
- `q016` **generation** (api: partial, local: partial) — 6,9 điểm là C+ hay B?  
  expected: C+ (2.5 hệ 4), vì B bắt đầu từ 7,0.  
  got: Đáp án: Không thể xác định chính xác là C+ hay B dựa trên các văn bản hiện có vì quy định của Trường Đại học Tôn Đức Thắng sử dụng thang điểm 10 làm chuẩn. Các điều kiện và hệ quả liên quan được nêu trong văn bản như sau: - Theo Bảng 1, xếp loại "Tru  
  cited: qc-dao-tao · Điều 24 khoản 1
- `q022` **generation** (api: partial, local: correct) — Học lại nhiều thì có bị hạ loại bằng không?  
  expected: Có, với loại giỏi và xuất sắc: bị giảm một mức nếu khối lượng môn phải học lại vượt quá 5% tổng số tín chỉ của chương trình (hoặc bị kỷ luật từ mức cảnh cáo trở lên).  
  got: Có, việc học lại nhiều sẽ dẫn đến việc hạ bậc xếp loại tốt nghiệp nếu khối lượng môn học phải học lại vượt quá 5% tổng số tín chỉ quy định cho toàn chương trình [1][3]. Các điều kiện và hệ quả cụ thể như sau: * **Điều kiện để hạ bậc:** Chỉ áp dụng đố  
  cited: tb-ha-bac-tot-nghiep · (không có mục), tb-ha-bac-tot-nghiep · (không có mục), qc-dao-tao · Điều 31 khoản 5, 6, qc-dao-tao · Điều 15
- `q029` **generation** (api: partial, local: partial) — Học kỳ đầu GPA bao nhiêu thì bị cảnh báo?  
  expected: ĐTBHK dưới 2,00 với học kỳ đầu của khóa học.  
  got: GPA (điểm trung bình chung) dưới **2,00** trong học kỳ đầu của khóa học sẽ khiến sinh viên bị cảnh báo kết quả học tập. Điều kiện cụ thể để áp dụng mức điểm này là: - Sinh viên phải còn trong thời hạn khóa học và không thuộc trường hợp trễ tiến độ [1  
  cited: qc-dao-tao · Điều 17 khoản 1
- `q030` **generation** (api: partial, local: partial) — Khi nào thì bị buộc thôi học?  
  expected: Bị cảnh báo kết quả học tập hai lần liên tiếp; vượt thời gian tối đa được phép học; bị kỷ luật xóa tên; hoặc hết thời hạn nghỉ học tạm thời mà không nhập học lại.  
  got: Sinh viên bị buộc thôi học khi thuộc một trong các trường hợp sau đây: 1. Bị cảnh báo kết quả học tập hai lần liên tiếp do rơi vào các trường hợp quy định tại khoản 1 Điều 17 (như không đạt tín chỉ, điểm trung bình thấp, không đăng ký môn học...) [1]  
  cited: qc-dao-tao · Điều 17 khoản 2, 3, 4, qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8, qc-dao-tao · Điều 17 khoản 1, phu-luc-vi-pham · (không có mục), phu-luc-vi-pham · (không có mục)
- `q034` **generation** (api: partial, local: partial) — Môn tiên quyết với môn học trước khác nhau chỗ nào?  
  expected: Môn tiên quyết A: phải học và đạt A mới được đăng ký B. Môn học trước A: chỉ cần đã học xong A (có thể chưa đạt) và được đăng ký B ở học kỳ tiếp sau.  
  got: Môn tiên quyết và môn học trước khác nhau về bản chất điều kiện ràng buộc đối với việc đăng ký học môn đó, cụ thể như sau: 1. **Về định nghĩa và điều kiện bắt buộc:** * **Môn tiên quyết:** Là môn học mà điều kiện bắt buộc để đăng ký học môn B là sinh  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 4 khoản 4, 5, qc-dao-tao · Điều 13 khoản 1, 2, qc-dao-tao · Điều 25 khoản 5, 6
- `q036` **generation** (api: partial, local: correct) — Rớt một môn tự chọn có bắt buộc phải học lại không?  
  expected: Không bắt buộc nếu đã tích lũy đủ số tín chỉ của nhóm tự chọn; có thể học lại môn đó hoặc chọn môn tự chọn khác cùng nhóm.  
  got: Không, sinh viên không bắt buộc phải học lại môn tự chọn nếu đã tích lũy đủ số tín chỉ của nhóm môn học tự chọn tương ứng; tuy nhiên, nếu chưa đạt điểm yêu cầu hoặc muốn cải thiện kết quả thì sinh viên có quyền đăng ký học lại. [1][2][3] **Chi tiết c  
  cited: qc-dao-tao · Điều 4 khoản 6, qc-dao-tao · Điều 3 khoản 1, 2, qc-dao-tao · Điều 15
- `q040` **generation** (api: partial, local: correct) — Vắng thi không phép thì điểm tính sao?  
  expected: Nhận điểm V, tính như điểm 0 và vẫn tính vào ĐTBHK, ĐTBTL; coi như đã dự thi một lần.  
  got: Vắng thi không phép được ghi nhận là "điểm V" (tương đương với "Không đủ điều kiện dự thi"), có giá trị tính như điểm 0 [4]. Điểm này sẽ được tính vào điểm trung bình học kỳ và điểm trung bình tích lũy, đồng thời không thuộc diện xét học bổng năm học  
  cited: qc-dao-tao · Điều 25 khoản 5, 6, qc-dao-tao · Điều 23, qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 24 khoản 2, qd-tieng-anh-clc · Điều 3
- `q042` **generation** (api: partial, local: partial) — Muốn bảo lưu vì lý do cá nhân thì cần điều kiện gì?  
  expected: Đã học tối thiểu 01 học kỳ, không thuộc diện bị xem xét buộc thôi học hoặc kỷ luật, ĐTBTL không dưới 5,00; thời gian nghỉ vẫn tính vào thời gian học tối đa.  
  got: Để sinh viên được bảo lưu kết quả học tập vì lý do cá nhân, phải đáp ứng các điều kiện sau: 1. Sinh viên phải nộp đơn xin nghỉ học tạm thời ít nhất 02 tuần trước khi học kỳ bắt đầu (theo kế hoạch thời gian năm học của Trường) [2]. 2. Sinh viên phải t  
  cited: qc-dao-tao · Điều 16 khoản 3, 4, qc-dao-tao · Điều 16 khoản 1, 2, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường, hd-hoc-bong · VIII. HỖ TRỢ PHẦN CHÊNH LỆCH HỌC PHÍ > 4. Lưu ý:
- `q053` **generation** (api: partial, local: partial) — Bị trùng lịch thi hai môn thì xin hoãn thi thế nào?  
  expected: Nộp đơn Hoãn thi trong thời gian quy định được công bố cùng lịch thi để được ghi nhận điểm H.  
  got: Để xin hoãn thi khi bị trùng lịch thi hai môn, sinh viên phải thực hiện các bước và đáp ứng điều kiện sau dựa trên quy định hiện hành: 1. **Nộp đơn:** Sinh viên phải nộp đơn "Hoãn thi" ngay khi sự việc phát sinh (trong thời gian quy định được công bố  
  cited: qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 25 khoản 2, qc-dao-tao · Điều 23, qc-dao-tao · Điều 22
- `q055` **generation** (api: partial, local: partial) — Chuẩn đầu ra tiếng Anh cần IELTS mấy chấm?  
  expected: Với chương trình chất lượng cao (khóa 2023 trở về sau): trình độ B2 quốc tế, IELTS ≥ 5.5 và tất cả kỹ năng ≥ 4.5 (hoặc TOEFL iBT ≥ 70, TOEIC 4 kỹ năng Nghe & Đọc ≥ 600, Viết ≥ 150, Nói ≥ 160). Chuẩn đ  
  got: Chuẩn đầu ra tiếng Anh cần IELTS từ **≥ 5.5** (tất cả kỹ năng ≥ 4.5) để đạt yêu cầu tối thiểu của sinh viên [2], hoặc **≥ 6.5** (tất cả kỹ năng ≥ 5.5) đối với ngành Ngôn ngữ Anh cụ thể [2]. Ngoài ra, mức điểm IELTS cũng được sử dụng làm điều kiện để   
  cited: qd-cu-nhan-uu-tu · II. Điều kiện được cấp Giấy chứng nhận Cử nhân/Kỹ sư ưu tú, hd-hoc-bong · VII. KHEN THƯỞNG > A. TẶNG GIẤY KHEN:, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ, qd-tieng-anh-clc · PHỤ LỤC 2. BẢNG XÉT MIỄN MÔN HỌC THEO CÁC LOẠI CHỨNG CHỈ TIẾNG ANH QUỐC TẾ
- `q057` **generation** (api: partial, local: correct) — Điểm rèn luyện toàn khóa tối thiểu bao nhiêu thì được tốt nghiệp?  
  expected: Điểm rèn luyện trung bình toàn khóa phải từ 50 điểm trở lên.  
  got: Điểm rèn luyện toàn khóa tối thiểu để xét tốt nghiệp là **50 điểm** (tương đương trung bình tích lũy toàn khóa từ 5,00 trở lên), áp dụng cho sinh viên Khóa tuyển sinh năm 2017 trở về sau; đối với Khóa tuyển sinh năm 2017 thì mức điểm này được áp dụng  
  cited: qc-ren-luyen · Điều 15 khoản 1, 2, 3, 4, qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8, qc-dao-tao · Điều 31 khoản 1, 2
- `q058` **generation** (api: partial, local: partial) — Đăng ký ký túc xá thế nào?  
  expected: Liên hệ Ký túc xá (tòa nhà K, ĐT (028) 37 760 652, ktx@tdtu.edu.vn), nơi tiếp nhận thủ tục đăng ký nội trú. Các bước đăng ký cụ thể không có trong các văn bản hiện có.  
  got: Để đăng ký ký túc xá, bạn cần liên hệ trực tiếp với phòng ban quản lý hoặc các đơn vị tổ chức hoạt động tại Ký túc xá. Cụ thể: 1. **Liên hệ trực tiếp:** Bạn có thể liên hệ để giải quyết thủ tục (như đăng ký nội trú, thanh lý hợp đồng, đăng ký gửi xe)  
  cited: phong-ban · 14. Ký túc xá, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 2. Học bổng áp dụng cho con, anh/chị em ruột của cán bộ công đoàn; 3. Học bổng sinh viên nội trú Ký túc xá, phong-ban · 1. Phòng Tổ chức hành chính:, hd-hoc-bong · II. HỌC BỔNG LƯU HỌC SINH; III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP, hd-hoc-bong · IX. HỖ TRỢ NGƯỜI HỌC > 2. Hỗ trợ một phần chi phí Ký túc xá tại Phân hiệu Khánh Hòa
- `q059` **hallucination**  — Thư viện mở cửa đến mấy giờ?  
  expected: Không tìm thấy trong các văn bản hiện có.  
  got: Không tìm thấy trong các văn bản hiện có thông tin về giờ mở cửa của Thư viện. Các đoạn trích chỉ đề cập đến việc giảng viên gửi yêu cầu tài liệu cho Thư viện trước khi bắt đầu môn học [1] và lưu trữ hồ sơ trên hệ thống tài nguyên của Thư viện [5], n  
  cited: qd-ung-dung-cong-nghe · Điều 13 khoản 2, qd-ung-dung-cong-nghe · Điều 9
- `q064` **generation** (api: incorrect, local: partial) — Điểm rèn luyện được chấm theo mấy nội dung, mỗi nội dung tối đa bao nhiêu điểm?  
  expected: 6 nội dung (học tập và học thuật; chấp hành nội quy; hoạt động chính trị - xã hội, văn hóa, thể thao; hoạt động cộng đồng, tình nguyện; tinh thần tiên phong, gương mẫu; điểm thưởng), mỗi nội dung tối   
  got: Điểm rèn luyện được chấm theo **7 nội dung**, mỗi nội dung có mức tối đa là **20 điểm**. Các nội dung và điều kiện tính điểm cụ thể như sau: 1. **Việc tham gia học tập và các hoạt động chuyên môn học thuật:** Tối đa 20 điểm, trong đó nếu xếp loại Kém  
  cited: qc-ren-luyen · Điều 3, qc-ren-luyen · Điều 10 khoản 2, 3, 4, qc-ren-luyen · Điều 10 khoản 1, qc-ren-luyen · Điều 8, qc-ren-luyen · Điều 4
- `q067` **generation** (api: partial, local: partial) — Bị xếp loại rèn luyện yếu hai học kỳ liên tiếp thì sao?  
  expected: Phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo; nếu bị yếu, kém hai học kỳ liên tiếp lần thứ hai thì bị buộc thôi học (ngoại lệ do Hội đồng quyết định).  
  got: Nếu sinh viên bị xếp loại rèn luyện yếu trong hai học kỳ liên tiếp, họ sẽ bị buộc thôi học nếu không thuộc trường hợp ngoại lệ do Hội đồng xem xét quyết định [1]. Ngoài ra, sinh viên phải tạm ngừng học ít nhất một học kỳ ở học kỳ tiếp theo sau mỗi lầ  
  cited: qc-ren-luyen · Điều 15 khoản 5, 6, 7, 8
- `q088` **generation** (api: partial, local: partial) — Hai anh em ruột cùng học ở trường thì có học bổng không?  
  expected: Có: 15% học phí theo khung chương trình tiêu chuẩn mỗi năm học, áp dụng từ người thứ hai; cấp vào cuối năm học.  
  got: Có, hai anh em ruột cùng học tại Trường Đại học Tôn Đức Thắng (TDTU) sẽ được xét cấp học bổng nếu thỏa mãn các điều kiện cụ thể sau đây: 1. **Đối tượng áp dụng:** Học bổng dành cho anh/chị em ruột đang học ngành chính tại Trường theo đúng khóa học [1  
  cited: hd-hoc-bong · IV. HỌC BỔNG KHÁC > 1. Học bổng anh/chị em ruột học tại Trường, hd-hoc-bong · IV. HỌC BỔNG KHÁC > 2. Học bổng áp dụng cho con, anh/chị em ruột của cán bộ công đoàn; 3. Học bổng sinh viên nội trú Ký túc xá, hd-hoc-bong · V. HỌC BỔNG ÁP DỤNG CHO PHÂN HIỆU > 3. Học bổng dành cho sinh viên là con ruột/em ruột của cựu sinh viên TDTU
- `q094` **generation** (api: partial, local: partial) — Em là người đầu tiên trong nhà học đại học thì có học bổng không?  
  expected: Có nếu trúng tuyển vào ngành thuộc nhóm thu hút 1, có đơn và xác nhận của địa phương: 20% học phí học kỳ 1 năm học 2025 - 2026; được xét tiếp các học kỳ sau nếu học tập, rèn luyện từ Khá và không bị k  
  got: Có, sinh viên là thế hệ đầu tiên trong gia đình học đại học sẽ được xét cấp học bổng 20% học phí theo khung chương trình đào tạo tiêu chuẩn học kỳ 1, năm học 2025 - 2026 [1]. Tuy nhiên, để được xét cấp học bổng này, sinh viên cần thỏa mãn các điều ki  
  cited: hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 13. Các nguyên tắc xét học bổng tân sinh viên
- `q096` **generation** (api: partial, local: correct) — Điểm môn tiếng Anh chương trình chất lượng cao tính thế nào?  
  expected: Thang điểm 100: điểm quá trình 60% + điểm thi cuối kỳ 40% (ĐTK = ĐQT + ĐCK).  
  got: Điểm môn tiếng Anh được đánh giá theo thang điểm 100 với hai thành phần: điểm đánh giá quá trình (ĐQT) chiếm tỷ trọng 60% và điểm thi cuối kỳ (ĐCK) chiếm tỷ trọng 40%. Điểm tổng kết (ĐTK) được tính bằng công thức cộng trực tiếp giữa hai thành phần nà  
  cited: qd-tieng-anh-clc · Điều 3, qd-tieng-anh-clc · PHỤ LỤC 3. HÌNH THỨC ĐÁNH GIÁ VÀ ĐIỀU KIỆN XÉT ĐẠT HỌC PHẦN TIẾNG ANH
- `q104` **generation** (api: incorrect, local: correct) — Đi thi trễ bao lâu thì không được vào phòng?  
  expected: Sau 15 phút kể từ khi tính giờ làm bài.  
  got: Theo quy định, thí sinh có mặt sau **15 phút** kể từ khi tính giờ làm bài thì không được phép vào phòng thi [1][3]. Ngoài ra, quy định còn nêu các điều kiện và ngoại lệ liên quan: - Thí sinh phải có mặt tại phòng thi trước giờ thi 30 phút để chuẩn bị  
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 1. Cán bộ coi thi, noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh, noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 1. Cán bộ coi thi
- `q106` **generation** (api: partial, local: correct) — Làm bài xong thì bao lâu được nộp bài ra về?  
  expected: Sau 1/2 thời gian thi.  
  got: Sinh viên được phép nộp bài và ra về sau **1/2 thời gian thi** nếu làm bài trên giấy, hoặc khi **hết giờ làm bài**. * Đối với sinh viên làm bài trên giấy: Sau 1/2 thời gian thi, TS được phép nộp bài làm cùng giấy thi, giấy nháp, đề thi và ra về [1].   
  cited: noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 3. Thí sinh, noi-quy-phong-thi · II. NHIỆM VỤ THỰC HIỆN > 1. Cán bộ coi thi
- `q112` **generation** (api: partial, local: partial) — Uống bia trong trường bị kỷ luật gì?  
  expected: Lần 1 cảnh cáo, lần 2 cảnh cáo lần 2, lần 3 đình chỉ học tập có thời hạn, lần 4 buộc thôi học.  
  got: Uống bia trong trường bị xử lý từ cảnh cáo đến buộc thôi học tùy thuộc vào số lần vi phạm tính trong cả khóa học, cụ thể như sau: Lần 1 và Lần 2 là Cảnh cáo; Lần 3 là Đình chỉ học tập có thời hạn; Lần 4 là Buộc thôi học [1]. Ngoài ra, nếu hành vi sử   
  cited: phu-luc-vi-pham · (không có mục)
- `q113` **generation** (api: incorrect, local: partial) — Bị trừ 25% điểm thi lần đầu thì có bị kỷ luật thêm không?  
  expected: Có: nghiêm khắc phê bình (lần 1), khiển trách (lần 2), ... đến buộc thôi học (lần 6).  
  got: Đáp án: Không có thông tin cụ thể về việc "bị kỷ luật thêm" khi chỉ bị trừ 25% điểm thi lần đầu trong các văn bản hiện có. Các điều kiện và quy định liên quan được nêu như sau: 1. Việc bị trừ 25% số điểm thi là hình thức xử lý thuộc **Mức 1** đối với  
  cited: phu-luc-vi-pham · (không có mục), noi-quy-phong-thi · III. XỬ LÝ VI PHẠM NỘI QUY PHÒNG THI > 2. Đối với Thí sinh, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:, hd-hoc-bong · I. HỌC BỔNG TÂN SINH VIÊN (KHÓA TUYỂN SINH NĂM 2025) > 7. Học bổng dành cho sinh viên là thế hệ đầu tiên trong gia đình học đại học, hd-hoc-bong · III. HỌC BỔNG KHUYẾN KHÍCH HỌC TẬP > 2. Điều kiện xét cấp học bổng khuyến khích học tập:

Causes: generation 22, hallucination 4, retrieval 1

