# Kiến trúc

`app/garden.tsx` là UI React dùng chung, bản local truyền `localMode`. `local/` là entry và cấu hình Vite; `public/` chứa PDF worker và tài liệu phát hành. Build tạo `local-app/public/`.

`local-app/server.mjs` nghe trên loopback, kiểm tra Host/Origin, phục vụ static và API. `/api/state` đọc/ghi SQLite với revision chống ghi đè; `/api/files` giữ tệp tối đa 20 MB; trạng thái tối đa 20 MB. `/api/health` có rootId để launcher phân biệt các bản app khác nhau. `/api/tts` tùy chọn proxy server VieNeu cố định cổng 8001 và cache WAV trong data; UI hiện dùng Web Speech en-US.

`app/model.ts` định nghĩa bài học, từ, tài liệu, tiến độ và lịch ôn. `curriculum-data.ts` chứa 52×200; `curriculum-legacy.ts` là snapshot để cập nhật chỉ các trường chưa bị người học sửa. Migration version 2 giữ tiến độ, fileId, sửa từ, câu và việc xóa bài. Mục cá nhân không bị thay thế.

`data/english-garden.sqlite`: bảng state giữ JSON và revision; bảng files giữ tên và ID tệp. `data/files/`: dữ liệu tệp gốc/ghi âm; không nằm trong GitHub. JSON backup chỉ chứa tham chiếu tệp. Với giáo trình mới, trạng thái thực tế khoảng 6.2 MB.

`start.ps1` tìm Node, kiểm tra server đúng rootId và thử các cổng; `.cmd` gọi launcher. `update.ps1` sao lưu dữ liệu, dừng đúng server theo đường dẫn rồi thay chương trình. Không xóa data khi cập nhật.

Mã cloud ở `app/api/` dùng auth ChatGPT, Cloudflare D1/R2, chưa triển khai. Giới hạn 1.8 MB của trạng thái cloud không đủ cho giáo trình mới. Không coi cloud là tính năng đã hoàn thiện; cần phân trang/chia record và thiết kế lại lưu từ/câu trước khi dùng.
