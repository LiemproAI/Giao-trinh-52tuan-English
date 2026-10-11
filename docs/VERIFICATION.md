# Kiểm tra và giới hạn xác nhận

Ngày tổng hợp: 2026-10-11. Bản local Node.js trên Windows.

- `tsc --noEmit`: đạt ở bản hiện tại.
- Vite build local: đạt. Bundle lớn khoảng 3.1 MB trước gzip do nhúng giáo trình; Vite cảnh báo kích thước chunk, chưa tối ưu chia tải.
- 14 test dữ liệu/API/import: đã đạt. Bao gồm CSV quoting và dấu Việt, trùng từ, lịch ôn, backup, 52 tuần, migration, file DOCX/DOC, CSV 200 câu, lưu qua restart, file CRUD, xung đột 409 và chặn Origin lạ.
- Sau sửa UI cuối: TypeScript và build đạt; API dữ liệu thật xác nhận 52 bài course và mọi bài đúng 200 câu. Chưa có kiểm thử thao tác browser tự động cho bản UI cuối vì công cụ browser bị chính sách chặn. Không suy từ build thành xác nhận UI trực tiếp.
- Migration dữ liệu thật: word edits, documents và progress được so sánh giữ nguyên; mọi tuần 200 câu; payload khoảng 6,208,178 byte. Không đưa snapshot dữ liệu thật vào repo.
- HTTP local trang và tài liệu HTML/ZIP mới: 200.
- VieNeu trước khi đổi giọng: health loaded=true, ID Hải Đăng xác minh từ voices, WAV có RIFF/WAVE, cache trả cùng bytes. Giọng hiện tại en-US: logic chọn giọng chỉ từ danh sách thật, ưu tiên giọng Mỹ; chưa nghe trực tiếp trên trình duyệt người dùng.
- Lint chưa đạt: lần kiểm tra trước có 47 lỗi (43 any, 4 cập nhật state trong effect) và 5 cảnh báo. Chưa xác nhận con số mới sau các thay đổi; không công bố lint sạch.
- Cloud chưa triển khai/kiểm thử end-to-end cho giáo trình mới. Không có URL production được xác nhận.
- Micro, OCR, chất lượng TTS và các PDF/DOC phức tạp cần kiểm tra trên máy người dùng. Chưa có đánh giá B2 được chuẩn hóa.

Lệnh chạy test và build nằm trong README. Test dùng dữ liệu riêng; khi kiểm tra app thật không ghi đè dữ liệu cá nhân.
