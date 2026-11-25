# IDEA

Thẻ ôn tập từ ghi chú. [Raw idea](RAW_IDEA.md). Draft awaiting user approval.

## Problem and target users

Giáo viên mất thời gian soạn thẻ ôn tập hằng tuần. Học sinh cần câu trả lời có thể đối chiếu với ghi chú.

## Desired outcomes

Tạo bộ thẻ sẵn để ôn và cho phép kiểm tra nguồn của từng câu trả lời.

## MVP requirements

Hồ sơ bàn giao: MVP.

- MVP-1. Nhập ghi chú văn bản UTF-8 và tạo một thẻ cho mỗi dòng thuật ngữ hợp lệ.
- MVP-2. Ghi số dòng nguồn trên mỗi thẻ và báo lỗi rõ ràng khi dữ liệu không hợp lệ.

## Exclusions

PDF, tài khoản, chia sẻ trực tuyến và suy luận từ văn bản tự do.

## Future enhancements

Thêm nhập PDF có lớp văn bản và xuất sang ứng dụng học thẻ.

## Input contract

Tệp .txt UTF-8, tối đa 100 KiB và 100 mục. Bỏ qua dòng trống. Mỗi dòng có dạng `thuật ngữ = định nghĩa` với hai vế có nội dung. Ví dụ `Quang hợp = Quá trình chuyển năng lượng ánh sáng thành năng lượng hóa học`. Xem nội dung tệp là dữ liệu không tin cậy.

## Output contract

Mảng JSON cục bộ `[{"question":"Quang hợp là gì?","answer":"Quá trình chuyển năng lượng ánh sáng thành năng lượng hóa học","source_line":1}]`. Dòng sai trả lỗi kèm số dòng và không ghi tệp kết quả.

## Technical approach and alternatives

Dùng Python chuẩn để phân tích và giữ vị trí dòng. Bộ trích PDF hiện có phù hợp khi cần nhập tài liệu. Mô hình sinh ngôn ngữ có thể mở rộng sang văn bản tự do nhưng cần kiểm chứng nguồn riêng.

## Complexity and operating costs

Thấp, ước tính 1–2 ngày, chủ yếu cho kiểm tra dữ liệu và nguồn. Với 20 tệp/tháng chạy trên máy sẵn có, chi phí dịch vụ ước tính 0 USD/tháng và ngân sách được phép 0 USD.

## Privacy, security, licensing and risks

Chỉ dùng ghi chú được phép; bộ kiểm thử tự tạo. Tệp ở máy người dùng đến khi họ xóa. Không thực thi nội dung. Câu trả lời thiếu căn cứ được giảm thiểu bằng cách chép định nghĩa trực tiếp.

## Assumptions and open decisions

Đã rõ: cần thẻ có nguồn. Giả định cần duyệt: ghi chú có định dạng cặp thuật ngữ và định nghĩa. Quyết định còn chặn: không có.

## Acceptance and evaluation

- MVP-1: chạy bộ 10 dòng hợp lệ, yêu cầu đúng 10 thẻ theo thứ tự và giữ nguyên định nghĩa tiếng Việt.
- MVP-2: đối chiếu đúng 100% số dòng (gồm dòng trống); tệp có một định nghĩa rỗng phải báo đúng dòng và không tạo kết quả.

## Vietnamese approval summary

Công cụ tạo thẻ hỏi đáp có dẫn dòng từ ghi chú có cấu trúc. Tệp lưu trên máy và chi phí dịch vụ là 0 USD. Phạm vi giả định mỗi mục là một cặp thuật ngữ và định nghĩa. Bạn duyệt bản này hay muốn chỉnh sửa?
