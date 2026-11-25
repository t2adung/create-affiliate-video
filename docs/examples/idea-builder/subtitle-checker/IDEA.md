# IDEA

Kiểm tra phụ đề trước khi đăng. [Raw idea](RAW_IDEA.md). Draft awaiting user approval.

## Problem and target users

Người dựng video hướng dẫn mất thời gian xem lại để tìm phụ đề chồng nhau.

## Desired outcomes

Trả danh sách lỗi có vị trí đủ rõ để người dựng sửa trực tiếp trong trình biên tập.

## MVP requirements

Hồ sơ bàn giao: MVP.

- MVP-1. Đọc tệp SRT và báo các cặp đoạn có thời gian chồng lấn.
- MVP-2. In kết quả có thể đọc và dùng mã thoát để phân biệt sạch, có lỗi thời gian và dữ liệu sai.

## Exclusions

Tự sửa phụ đề, tạo phụ đề từ âm thanh, dịch và đăng video.

## Future enhancements

Thêm kiểm tra tốc độ đọc và xuất báo cáo CSV.

## Input contract

Tệp .srt UTF-8 tối đa 2 MiB hoặc 1.000 đoạn. Dùng số thứ tự dương duy nhất và mốc `HH:MM:SS,mmm --> HH:MM:SS,mmm`, thời điểm kết thúc phải lớn hơn bắt đầu. Ví dụ đoạn 1 từ 00:00:01,000 đến 00:00:03,000.

## Output contract

In một dòng cho mỗi cặp, ví dụ `Cue 1 overlaps cue 2 by 500 ms`. Theo thứ tự tăng của vị trí xuất hiện các cặp trong tệp. Mã 0 nếu sạch, 1 nếu chồng lấn, 2 nếu không đọc được hoặc sai cấu trúc. Lỗi dữ liệu ghi vào stderr kèm số dòng nếu xác định được và không in báo cáo từng phần.

## Technical approach and alternatives

Dùng trình phân tích SRT nhỏ trong Python chuẩn và đối chiếu mốc thời gian theo mili giây. Thư viện SRT đáng cân nhắc nếu sau này cần hỗ trợ nhiều biến thể. FFmpeg hữu ích nếu bổ sung kiểm tra dựa trên độ dài video.

## Complexity and operating costs

Thấp, ước tính 1–2 ngày để xử lý mốc thời gian và ca biên. Với 30 tệp/tháng chạy trên máy sẵn có, chi phí dịch vụ ước tính 0 USD/tháng và ngân sách được phép 0 USD.

## Privacy, security, licensing and risks

Chạy cục bộ, chỉ in số đoạn và thời gian, không lưu nội dung phụ đề. Dùng SRT tự soạn trong kiểm thử. Dùng số nguyên mili giây để tránh lỗi làm tròn; các đoạn tiếp giáp được chấp nhận.

## Assumptions and open decisions

Đã rõ: báo chỗ chồng lấn trước khi đăng. Câu hỏi mẫu: báo hay tự sửa? Câu trả lời mô phỏng: chỉ báo. Giả định cần duyệt: dùng SRT và kiểm tra qua dòng lệnh. Quyết định còn chặn: không có.

## Acceptance and evaluation

- MVP-1: với đoạn 1 (1–3 giây), đoạn 2 (2,5–4 giây) và đoạn 3 (4–5 giây), chỉ báo cặp 1–2 với 500 ms.
- MVP-2: fixture sạch trả 0, fixture chồng lấn trả 1, fixture có thời gian ngược trả 2 và ghi lỗi vào stderr.

## Vietnamese approval summary

Công cụ sẽ chỉ ra các đoạn SRT chồng nhau để bạn tự sửa trước khi đăng. Công cụ chạy trên máy, không in nội dung phụ đề và dự kiến không có phí dịch vụ. Bạn duyệt bản này hay muốn chỉnh sửa?
