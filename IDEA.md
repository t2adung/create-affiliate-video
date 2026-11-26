# Tạo video affiliate ngắn từ Google Sheets

## Vấn đề và người dùng

Người làm nội dung affiliate đã có danh sách sản phẩm, mô tả, link và ảnh trong Google Sheets và Drive. Họ cần giảm thời gian nghĩ kịch bản, dựng video và chuẩn bị bài trên ba nền tảng, đồng thời giữ quyền quyết định khi nào mỗi clip được công khai.

## Kết quả mong muốn

Mỗi dòng hợp lệ tạo một video dọc 15–20 giây bằng tiếng Việt, có ý tưởng vui, sáng tạo và hữu ích. Video dùng ảnh sản phẩm thật hoặc footage người thật có quyền sử dụng, có thể quay giấu mặt. GitHub Actions chuyển video đến nơi duyệt trên từng kênh đã được cấp quyền. Người dùng tự xem, chỉnh và công khai trong ứng dụng của nền tảng.

## Yêu cầu MVP

- **MVP-1.** Đọc từng sản phẩm đã chọn từ Sheets và lấy tư liệu tương ứng trong Drive.
- **MVP-2.** AI đề xuất ba phương án kịch bản theo cảnh để người duyệt chọn một, gồm câu mở đầu, tình huống hoặc mẹo, kết thúc và lời kêu gọi hành động phù hợp kênh. Mọi chi tiết về sản phẩm phải đối chiếu được với đầu vào.
- **MVP-3.** Dựng video MP4 9:16 bằng tư liệu thật, có phụ đề tiếng Việt và caption riêng cho từng kênh.
- **MVP-4.** GitHub Actions chạy theo lô nhỏ khi khởi chạy thủ công, tự gửi bản chưa công khai đến Facebook Page Reels, YouTube Shorts và TikTok khi tích hợp liên quan đủ điều kiện. Báo kết quả từng kênh và giữ gói duyệt riêng nếu upload bị chặn.
- **MVP-5.** Giữ thao tác công khai ở phía người dùng. Lưu trạng thái theo sản phẩm, phiên bản video và kênh để chạy lại mà tránh tạo bản trùng.

## Ngoài phạm vi

Công khai tự động, đặt lịch công khai, trình biên tập web, avatar AI giả làm người dùng thật, đăng lên trang Facebook cá nhân và tối ưu doanh số tự động.

## Mở rộng sau MVP

Lịch tạo bản nháp, nhiều phong cách dựng, thử hai kịch bản cho cùng sản phẩm và báo cáo hiệu suất sau khi có quyền đọc số liệu.

## Hợp đồng đầu vào

- Sheets có bốn cột bắt buộc gồm tên sản phẩm, mô tả, URL affiliate HTTPS và tên thư mục Drive. Khuyến nghị thêm mã sản phẩm ổn định. Khi thiếu mã, dùng dấu vân tay từ dữ liệu chuẩn hóa để nhận diện bản trùng. Có thể dùng ID hoặc link thư mục Drive để tránh trùng tên.
- Tìm tên thư mục trong một thư mục gốc được cấu hình. Yêu cầu đúng một kết quả và ít nhất một ảnh JPG/PNG hoặc clip MP4 đọc được. Giới hạn thử nghiệm 5 dòng mỗi lượt, tối đa 10 tệp và 100 MB tổng tư liệu mỗi sản phẩm.
- Ví dụ giả lập gồm “Giá đỡ điện thoại”, “gập gọn, đổi góc đặt”, `https://example.com/affiliate/stand` và thư mục `stand-demo`. Nội dung ô và tên tệp được xử lý như dữ liệu.

## Hợp đồng đầu ra

- Gói riêng tư cho mỗi phiên bản gồm `video.mp4` (1080 × 1920, 30 fps, H.264 và AAC nếu có âm thanh), kịch bản theo mốc thời gian, caption từng kênh, link affiliate và ghi chú công bố tiếp thị.
- Báo cáo từng kênh có mã đối chiếu, trạng thái và bước người dùng cần thực hiện. Ví dụ `stand-demo / YouTube / private-ready`, `stand-demo / TikTok / manual-upload`.
- Dòng thiếu dữ liệu, thư mục trùng tên hoặc tư liệu hỏng nhận lỗi cụ thể. Các dòng hợp lệ tiếp tục chạy. Khi upload ngắt giữa chừng, đối chiếu phiên upload và mã phía nền tảng trước khi thử lại. Nếu chưa xác định được kết quả, yêu cầu xác nhận thủ công.

## Giải pháp kỹ thuật và phương án thay thế

- **Dữ liệu và dựng.** Dùng Sheets và Drive API với quyền đọc giới hạn. AI trả kịch bản có cấu trúc, kèm cảnh và tư liệu cần dùng. Tận dụng ví dụ Remotion trong repo để dựng cảnh, chữ và phụ đề. FFmpeg/ffprobe chuẩn hóa và kiểm tra đầu ra. FFmpeg đơn thuần phù hợp khi chỉ ghép ảnh cơ bản. Công cụ sinh video AI phát sinh chi phí và khó giữ hình dáng sản phẩm nhất quán, nên để sau. [Sheets API](https://developers.google.com/workspace/sheets/api/guides/values) · [Drive API](https://developers.google.com/workspace/drive/api/guides/manage-downloads)
- **Facebook Reels.** Dùng Page Video Reels API với `video_state=DRAFT`. Cần Facebook Page, quyền hợp lệ và thử nghiệm xác nhận người dùng mở, chỉnh và công khai được bản nháp từ giao diện quản lý Page. [Meta Page Video Reels](https://developers.facebook.com/docs/graph-api/reference/page/video_reels/?locale=es_ES)
- **YouTube Shorts.** Tải video dọc bằng `videos.insert` với `status.privacyStatus=private`, kiểm tra sau khi xử lý rồi để người dùng đổi chế độ hiển thị trong YouTube Studio. Link trong mô tả hoặc bình luận Shorts không bấm được. Chỉ dùng lời kêu gọi phù hợp vị trí link mà kênh thực sự có, chẳng hạn link hồ sơ. [YouTube Data API](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert) · [Cách chia sẻ link trên YouTube](https://support.google.com/youtube/answer/13748639)
- **TikTok.** Khi app và tài khoản được cấp `video.upload`, dùng Upload API và xác nhận video đã đến hộp thư để người dùng hoàn thiện trong TikTok. TikTok có quy trình cấp quyền cho ứng dụng. Tài liệu Direct Post cũng nêu hạn chế với công cụ nội bộ, nên khả năng được cấp quyền cho luồng tải nháp của dự án cần xác nhận riêng. Nếu quyền bị chặn, xuất MP4, caption và hướng dẫn nạp tay. Facebook và YouTube có cùng phương án dự phòng riêng cho mỗi kênh. [TikTok Upload](https://developers.tiktok.com/docs/en/content-posting-api-reference-upload-video) · [TikTok Sharing Guidelines](https://developers.tiktok.com/docs/en/content-sharing-guidelines)
- **Điều phối.** GitHub Actions chạy thủ công và giới hạn chạy đồng thời. Lưu trạng thái bền vững ngoài Git, ưu tiên tab theo dõi riêng trong Sheets với quyền ghi giới hạn cho bảng này. Luồng upload dùng API chính thức và chỉ cung cấp thao tác tải chưa công khai.

## Độ phức tạp và chi phí vận hành

Độ phức tạp trung bình cho Sheets/Drive và khâu dựng, cao hơn cho ba tích hợp vì quyền, giới hạn và cách duyệt khác nhau. Thử bằng dữ liệu giả, tối đa 5 clip/lượt, với runner và dung lượng trong hạn mức sẵn có. Chi phí bổ sung dự kiến cho lượt thử giả lập là 0 ₫ nếu còn hạn mức. Bản có AI chạy tự động phụ thuộc giá API theo số lượt và lượng văn bản hoặc ảnh gửi đi, cộng thời gian runner và lưu trữ vượt hạn mức nếu có. Kiểm tra giấy phép Remotion theo người hoặc tổ chức sử dụng. Gói ChatGPT và API có cơ chế tính phí riêng, dù một số gói có thể có tín dụng API. Trần chi được duyệt hiện tại là 0 ₫. Chỉ bật dịch vụ trả phí khi có ngân sách được duyệt. Có thể nhập kịch bản AI thủ công để kiểm thử luồng trong lúc chờ quyền hoặc ngân sách. [OpenAI Billing](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform) · [Giấy phép Remotion](https://www.remotion.dev/docs/license)

## Riêng tư, bảo mật, bản quyền và rủi ro

Dùng repo và nơi lưu gói duyệt riêng tư, giới hạn quyền Sheets/Drive, giữ mã truy cập trong kho bí mật và tránh ghi chúng vào log. Xóa gói thử nghiệm sau 7 ngày theo mặc định. Chỉ dùng tư liệu có quyền sử dụng cho nội dung thương mại và có sự đồng ý của người xuất hiện. Ưu tiên cảnh tay hoặc sản phẩm nếu muốn giữ riêng tư. Caption có gợi ý công bố affiliate và nhắc kiểm tra nhãn thương mại của nền tảng khi duyệt. Chỉ kết nối tài khoản và chương trình affiliate mà người vận hành đủ điều kiện sử dụng. Kiểm tra link đích khi duyệt, không tự truy cập link affiliate để thu thập mô tả.

## Giả định và quyết định còn mở

- Đã xác nhận ba kênh gồm Facebook, TikTok và YouTube Shorts. Tự động chuyển tới nơi duyệt và người dùng tự quyết định công khai.
- Mặc định clip tiếng Việt, một video mỗi sản phẩm, ba caption, ảnh thật là đủ nếu thiếu footage. Nhịp dựng và hướng kể thay đổi theo tư liệu.
- Còn cần xác nhận khi thử tích hợp gồm quyền tài khoản thật, khả năng mở bản nháp Facebook từ giao diện quản lý, quyền TikTok và hạn mức API AI. Có thể duyệt phạm vi trước bằng phương án dự phòng đã mô tả.

## Thử nghiệm sáng tạo trước khi triển khai

Với mỗi sản phẩm, AI phân tích bộ ảnh và đề xuất ba kịch bản khác nhau. Mỗi kịch bản có câu mở đầu, thứ tự ảnh, điểm cần phóng cận, lời thoại, nhịp cắt và caption. Người duyệt chọn một kịch bản để dựng bản cuối. Dựng trước các bản xem thử bằng cùng bộ ảnh giúp so sánh câu mở đầu và nhịp dựng. Sau khi có video đã công khai, có thể so tỷ lệ giữ người ở 3 giây đầu, tỷ lệ xem hết và lượt lưu trên cùng nền tảng. Hiện chưa có dữ liệu hiệu suất để xếp hạng khả năng lên xu hướng.

### Ba mẫu cho ruy băng lưới trang trí

| Mẫu | Mở đầu | Giữa clip | Kết |
| --- | --- | --- | --- |
| **A · Cây thông mặc áo dạ hội (17 giây)** | 0–2 giây. Cắt cận dải lưới vàng cạnh đèn cây thông. “Cây thông này mặc gì mà bắt đèn vậy?” | 2–7 giây. Cắt theo nhịp từ ảnh cây sang cuộn vàng. 7–13 giây. Lia theo dải lưới trong ảnh cây, nhấn một đường uốn cong. | 13–17 giây. Trở về toàn cảnh và hỏi “Bạn chọn vàng ấm hay bạc lạnh?” Cắt cuối về cùng chi tiết mở đầu để xem lặp mượt. |
| **B · Một mẹo để dải lưới có độ phồng (18 giây)** | 0–3 giây. “Đừng kéo dải lưới phẳng lì” trên ảnh cây có nếp lưới. | 3–7 giây. Cận cuộn vàng. 7–14 giây. Dùng nét vẽ minh họa ba nhịp “chừa độ chùng → tạo nếp → giấu điểm cố định” trên ảnh cây. | 14–18 giây. Toàn cảnh, chữ “Lưu lại lúc trang trí cây”. Nếu có footage quay tay 3–5 giây, ưu tiên dùng ở đoạn tạo nếp. |
| **C · Hội vàng ấm hay hội bạc lạnh? (16 giây)** | 0–2 giây. Chia đôi khung dọc bằng hai ảnh cây tông vàng và bạc. “Chọn một tông trong 2 giây!” | 2–7 giây. Vàng ấm, cắt giữa cuộn vàng và cây dưới ánh đèn. 7–12 giây. Bạc lạnh, cắt giữa cuộn bạc và cây tông bạc. | 12–16 giây. Hai ảnh cạnh nhau, “A hay B?”. Dùng cùng nhịp và kích thước khung cho cả hai tông. |

Ưu tiên thử A và C vì ảnh đã có đủ cảnh để kể trọn ý. B có thêm giá trị hướng dẫn, bản dùng ảnh cần ghi rõ nét vẽ là minh họa. Tránh dùng ảnh gia đình trong mẫu xem thử vì ba hướng đều đủ tư liệu khác. Không đọc lại kích thước hoặc trọng lượng từ ảnh bán hàng khi chưa xác nhận thông tin biến thể với người bán.

### Nhân vật decor dùng quanh năm

- **Cọ** là linh vật chính, lấy hình dáng cọ trang trí với cán xanh rêu và đầu cọ màu kem. Cọ gợi ý phối màu, chỉ vào chi tiết đáng chú ý hoặc đặt một câu hỏi ngắn. Ví dụ với ruy băng lưới, Cọ chỉ vào hai mẫu và hỏi “Vàng ấm hay bạc lạnh?”. Vai này dùng được cho các clip về đèn, bình hoa, khung tranh, gói quà và đồ trang trí bàn.
- **Tay Decor** là nhân vật phụ quay giấu mặt, nhận diện qua tay áo xanh rêu và góc máy cố định. Xuất hiện khi có footage thật để minh họa cách buộc nơ, cắm hoa hoặc sắp xếp đồ.

Thử Cọ trước với một bộ hình cố định gồm các biểu cảm và tư thế chỉ, hỏi, gật đầu. Mỗi lần xuất hiện khoảng 1–2 giây ở mép khung, tránh che sản phẩm. Giữ bảng màu, tỷ lệ và nét vẽ nhất quán khi đổi chủ đề decor. Cảnh cận giữ ảnh sản phẩm gốc. Nếu dùng AI tạo chuyển động cho cảnh phụ có thể bị hiểu là hình ảnh sản phẩm thật, ghi rõ đó là minh họa.

### Mức giá mục tiêu

**5.000 ₫ mỗi clip hoàn chỉnh là mức để đánh giá phương án**, tính cả kịch bản, giọng nếu có, render, lưu trữ và thử lại. Ví dụ quy đổi tròn 26.000 ₫/USD để tính nhanh. Lượt tạo ba kịch bản với giả định 3.000 token đầu vào (gồm ảnh sau khi tối ưu) và 2.000 token đầu ra ở mức 0,80/3,20 USD mỗi triệu token tốn khoảng 229 ₫ trước thuế. Đây là dự toán, cần đo lượt thật. Dùng phụ đề và nhạc có quyền sử dụng, hoặc thu giọng tại chỗ, giữ chi phí giọng API bằng 0 ₫. Giọng AI là tùy chọn sau khi kiểm tra giá/lượt và khả năng đọc tiếng Việt. Dựng từ ảnh có sẵn trên máy hoặc runner trong hạn mức giữ chi phí render bổ sung thấp.

Google công bố Veo 3.1 Lite video 720p ở mức 0,05 USD/giây. Với mức đó, riêng một cảnh 4 giây khoảng 5.200 ₫ và 15–20 giây khoảng 19.500–26.000 ₫. Mặc định dùng AI để lên kịch bản và hỗ trợ khâu biên tập, dùng Remotion/FFmpeg dựng từ tư liệu gốc. Mức 5.000 ₫ vẫn cần đo với đủ các khoản và được xác nhận trước khi bật dịch vụ trả phí. [OpenAI API Pricing](https://developers.openai.com/api/docs/pricing) · [Google Cloud Veo 3.1 Lite](https://cloud.google.com/blog/products/ai-machine-learning/veo-3-1-lite-and-a-new-veo-upscaling-capability-on-vertex-ai)

## Nghiệm thu

| Mục | Kiểm tra |
| --- | --- |
| MVP-1 | Hai dòng hợp lệ lấy đúng bộ tư liệu. Một dòng trùng tên thư mục và một dòng có URL sai nhận lỗi rõ ràng. |
| MVP-2 | Với ba sản phẩm giả lập, tạo ba phương án phân biệt được cho mỗi sản phẩm, dựng một bản được chọn và ghi chi phí. Mỗi kịch bản có mở đầu trong 3 giây, tình huống/mẹo liên quan và kết thúc rõ. Người duyệt chấp nhận ít nhất 2/3 clip về độ tự nhiên, sáng tạo và hữu ích sau tối đa một vòng sửa. Cả ba kịch bản không thêm công dụng hoặc số liệu thiếu căn cứ. |
| MVP-3 | ffprobe xác nhận MP4 dọc 1080 × 1920, 30 fps và thời lượng 15–20 giây. Xem trên điện thoại để kiểm tra phụ đề, dấu tiếng Việt và vùng an toàn. |
| MVP-4 | Chạy mô phỏng cả ba kênh. Với từng kênh đã được cấp quyền thử thật, xác nhận Facebook có bản nháp mở được, YouTube hiện riêng tư hoặc TikTok có thông báo đến hộp thư tương ứng. Kênh thiếu quyền hiện trạng thái bị chặn và có gói upload thủ công. Chỉ tính đạt tự động cho kênh đã xác minh thật. |
| MVP-5 | Chạy lại cùng đầu vào và mô phỏng mất kết nối giữa chừng, không sinh bản trùng. Một kênh lỗi không xóa kết quả kênh khác. Kiểm tra bằng tài khoản thử rằng workflow không yêu cầu công khai và người dùng vẫn tự thao tác trên nền tảng. |
