# English Garden — Giáo trình 52 tuần

Bản V1.1 chạy cục bộ trên Windows: **52 tuần × 200 câu Anh–Việt = 10.400 câu**, mỗi tuần có 10 nhóm luyện, mỗi nhóm 20 câu. Mục tiêu lộ trình là tiến tới B2; đạt B2 cần đánh giá năng lực thực tế, không chỉ hoàn thành câu mẫu.

## Dùng ngay

1. Tải [English-Garden-App-v1.1-52-Tuan.zip](outputs/English-Garden-App-v1.1-52-Tuan.zip) và giải nén toàn bộ vào một thư mục.
2. Cài Node.js **22.13 trở lên** nếu máy chưa có. Máy phát triển đã chạy Node.js 24.14.1.
3. Nhấn đúp `MO-GIAO-TRINH-52-TUAN.cmd` hoặc `MO-APP.cmd` trong thư mục đã giải nén.
4. Dùng địa chỉ launcher hiển thị. Cổng đầu tiên là `http://127.0.0.1:4173/`; nếu bận launcher chọn cổng khác.
5. Chọn tuần: mặc định mở Phrases và toàn bộ 200 câu; chọn nhóm để luyện từng bộ 20 câu.

Sau khi bật lại máy cần chạy launcher. Địa chỉ 127.0.0.1 chỉ dùng trên máy đang chạy app. Không cần tài khoản cho bản local. Nếu trang cũ còn trong trình duyệt, dùng Ctrl+Shift+R.

## Chức năng đã có

- 52 chủ đề đời sống, đi lại, công việc, giao tiếp xã hội và thảo luận; lịch học bảy ngày, nhiệm vụ áp dụng, kiểm tra chặng tuần 13/26/39/52.
- 10 tab: mẫu câu, Phrases, Flashcards, phản xạ 3 giây, mở rộng câu, Roleplay, Rapid Fire, Q&A, bài tập, nộp bài tự luyện.
- Nhập PDF, DOCX, DOC, TXT, CSV, TSV; nhập/dán văn bản và clipboard, xem trước rồi chọn nội dung để lưu.
- Kho từ vựng: thêm/sửa/xóa/tìm/lọc/xuất CSV; 50 mục mỗi trang. Ôn tập tối đa 40 thẻ mỗi phiên và lên lịch theo mức nhớ.
- Tài liệu: đọc, nghe, sửa, copy, chọn phần bôi đen để thêm vào kho; lưu tệp gốc.
- Ghi âm hoặc tải bản luyện nói; tự đánh dấu hoàn thành, ghi chú và lưu tiến độ.
- SQLite và thư mục tệp cục bộ; lưu tự động, phát hiện xung đột cửa sổ, sao lưu/khôi phục JSON và nâng cấp giữ dữ liệu cũ.
- Giọng Anh–Mỹ en-US: ưu tiên Aria/Jenny/Guy nếu trình duyệt có cung cấp, tốc độ mặc định 0.9×, cho phép chọn/nghe thử trong Cài đặt. Không yêu cầu VieNeu để dùng giọng hiện tại.

200 câu là một ngân hàng bài luyện chuyển mẫu vào 10 hành động thực tế. Cấu trúc được lặp lại giữa nhóm/tuần có chủ đích; không phải 10.400 cấu trúc ngữ pháp độc lập. Nhóm luyện tác động tới Phrases, flashcards, phản xạ và Rapid Fire; mẫu câu hiện ba câu tiêu biểu, hội thoại/bài tập có nội dung riêng.

## Tài liệu

- [Sách HTML đầy đủ 10.400 câu](outputs/Tieng-Anh-52-Tuan-10400-Cau.html): tải và mở bằng trình duyệt.
- [52 bộ CSV/TXT và hướng dẫn B2](outputs/Giao-Trinh-52-Tuan-200-Cau.zip).
- [File mẫu nhập app](outputs/Bo-Mau-Nhap-App.zip).
- `outputs/Tieng-Anh-My-52-Tuan.pdf`: sách nền tảng 125 trang của bản đầu, mỗi tuần sáu câu gốc; **không phải sách PDF 10.400 câu**.

## Phát triển

Mã nguồn nằm tại `outputs/english-app/`. Bản local dùng React/Vite và server Node.js có SQLite; các route Cloudflare D1/R2 trong mã nguồn là phần chuẩn bị cho bản cloud.

```powershell
cd outputs/english-app
npm ci
npx tsc --noEmit
npx vite build --config local/vite.config.ts
cd local-app
powershell -NoProfile -ExecutionPolicy Bypass -File start.ps1
```

Build sao chép tài nguyên `public/` vào `local-app/public/`. Không sửa bundle trong ZIP để phát triển; sửa `app/` rồi build lại. Kiểm thử:

```powershell
cd outputs/english-app
node --experimental-strip-types --test tests/core.test.mjs tests/curriculum.test.mjs tests/upgrade-200.test.mjs tests/import.test.mjs tests/local-api.test.mjs
```

Test API dùng cổng 4191 và thư mục dữ liệu test riêng; không dùng dữ liệu học thật.

`work/` chứa nguồn biên soạn, dữ liệu giáo trình và công cụ dựng tài liệu. `expand_200.py` tạo ngân hàng câu và CSV/TXT/HTML; `build_curriculum.py` dựng sách gốc, cần Python/reportlab và font Arial trên Windows. Các script `integrate_*` là bước chuyển bản một lần, không chạy lại trên mã nguồn hiện tại.

## Lưu dữ liệu và cập nhật

Dữ liệu của người học nằm trong `data/` cạnh server của bản đã giải nén. Chờ “Đã đồng bộ” trước khi đóng trang. Sao lưu đầy đủ: dừng app rồi sao chép thư mục `data/`; JSON không chứa nội dung các tệp ghi âm/tài liệu gốc.

Để cập nhật bản đã dùng, giải nén ZIP mới vào thư mục khác, chạy `CAP-NHAT-V1.1.cmd`, chọn thư mục app cũ. Công cụ sao lưu rồi thay chương trình, giữ `data/`. Các sửa đổi câu, nghĩa từ, lịch ôn, bài cá nhân và tham chiếu ghi âm được giữ; mục đã xóa ở giáo trình cũ không tự phục hồi. Dấu hoàn thành cũ không có nghĩa đã luyện hết 200 câu bổ sung.

## Giới hạn hiện tại

- Chưa triển khai website cloud công khai hoặc đồng bộ nhiều thiết bị. Route cloud có giới hạn trạng thái khoảng 1.8 MB, **chưa hỗ trợ toàn bộ giáo trình mới khoảng 6.2 MB**; cần thiết kế lưu trữ chia nhỏ trước khi triển khai cloud.
- Chưa có AI dịch, chấm phát âm, giáo viên nhận bài hay chứng nhận B2. Chấm điền từ dựa trên đáp án mẫu; cần luyện với người khác và đánh giá độc lập.
- Giọng tự nhiên phụ thuộc danh sách giọng thực tế của trình duyệt; chưa xác nhận bằng nghe trực tiếp chất lượng âm thanh trên máy người dùng.
- PDF tối đa 100 trang/tệp, mỗi tệp 20 MB; OCR Anh/Việt cần tải bộ nhận dạng. DOC có mật khẩu/RTF/định dạng cũ đặc biệt cần chuyển DOCX. Trạng thái bản local tối đa 20 MB.
- TTS VieNeu Hải Đăng còn endpoint tùy chọn `/api/tts` và module trong mã nguồn, nhưng đã ngừng dùng làm giọng mặc định theo feedback. Âm thanh WAV tạo thử và cache cá nhân không có trong repository.
- TypeScript, build local và 14 kiểm thử đã đạt; ESLint còn lỗi từ mã hiện tại. Chi tiết ở [báo cáo kiểm tra](docs/VERIFICATION.md).

## Hồ sơ dự án

- [Tổng hợp feedback và cách xử lý](docs/FEEDBACK.md)
- [Lịch sử phiên bản](CHANGELOG.md)
- [Kiến trúc và dữ liệu](docs/ARCHITECTURE.md)
- [Báo cáo kiểm tra](docs/VERIFICATION.md)

Tiêu chí tham chiếu: [CEFR B2 — Council of Europe](https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale). Không có dữ liệu học cá nhân, tài khoản, token, cache và bản ghi âm trong repository này.
