from pathlib import Path
import csv, zipfile

out = Path('outputs/Mau-Nhap-Tai-Lieu')
out.mkdir(parents=True, exist_ok=True)
rows = [
 ('Could you take a look at this?', 'Bạn xem giúp cái này được không?'),
 ('My laptop keeps freezing.', 'Máy tính của tôi cứ bị treo.'),
 ('The screen is completely blank.', 'Màn hình hoàn toàn không hiển thị gì.'),
 ('When did the problem start?', 'Vấn đề bắt đầu khi nào?'),
 ('It started this morning.', 'Nó bắt đầu sáng nay.'),
 ('Have you tried restarting it?', 'Bạn đã thử khởi động lại chưa?'),
 ('I already restarted it twice.', 'Tôi đã khởi động lại hai lần rồi.'),
 ('Could you walk me through the steps?', 'Bạn hướng dẫn tôi từng bước được không?'),
 ('Let me back up my files first.', 'Để tôi sao lưu các tệp trước đã.'),
 ('How long will the repair take?', 'Việc sửa chữa sẽ mất bao lâu?'),
 ('Is the repair covered by the warranty?', 'Việc sửa chữa có nằm trong bảo hành không?'),
 ('Please let me know when it is ready.', 'Khi nào xong thì báo cho tôi nhé.'),
]
with (out/'Mau-Tu-Vung.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['English', 'Vietnamese'])
    writer.writerows(rows)
plain = '\n'.join(f'{en} | {vi}' for en, vi in rows) + '\n'
(out/'Mau-Bai-Hoc.txt').write_text(plain, encoding='utf-8-sig')
(out/'Huong-Dan.txt').write_text('''FILE MẪU NHẬP VÀO ENGLISH GARDEN V1.1

1. NHẬP TỪ VỰNG
Mở app → Nhập nội dung → chọn Mau-Tu-Vung.csv.
Chọn Kho từ vựng → Xem trước nội dung → Lưu vào ứng dụng.
CSV có hai cột English và Vietnamese; mỗi dòng là một từ hoặc câu.
Bạn có thể sửa bằng Excel rồi lưu dạng CSV UTF-8.
Chỉ hai cột đầu được nhập; ví dụ và nhãn có thể bổ sung trong Kho từ vựng.

2. NHẬP BÀI HỌC
Chọn Mau-Bai-Hoc.txt → đặt tên “Nhờ hỗ trợ và sửa máy tính”.
Chọn Bài học mới → Xem trước nội dung → Lưu vào ứng dụng.
Vào Bài học → chọn bộ Bài cá nhân & bài mẫu cũ để tìm bài đã nhập.
Mỗi dòng dùng định dạng: Câu tiếng Anh | Nghĩa tiếng Việt.
Không thêm tiêu đề, hướng dẫn hoặc số thứ tự vào file mẫu TXT.
Có thể mở TXT bằng Notepad, thay nội dung và lưu UTF-8.
Hoặc sao chép nội dung TXT rồi dán Ctrl+V vào ô Nội dung của app.

3. NHẬP TÀI LIỆU ĐỂ ĐỌC
Cũng có thể chọn file TXT và chọn Tài liệu học tập để giữ nguyên văn.
PDF và DOCX được đọc thành văn bản; chúng không tự tạo đủ mọi tab bài học.
Bài học mới tạo từ các câu nhập; bạn bổ sung hội thoại, mẫu câu và đáp án qua Sửa bài.

4. LƯU VÀ CẬP NHẬT
Chờ app hiện “Đã đồng bộ” trước khi đóng trang.
Nội dung đã nhập được giữ trong dữ liệu app trên máy này.
Nhập lại từ/câu tiếng Anh đã có sẽ bỏ qua mục trùng, không cập nhật nghĩa cũ.
Muốn sửa nghĩa: vào Kho từ vựng → Sửa → Lưu.
Đây là bộ mẫu, không cần nhập file Huong-Dan.txt vào kho.
''', encoding='utf-8-sig')
with zipfile.ZipFile('outputs/Bo-Mau-Nhap-App.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for path in out.iterdir():
        z.write(path, path.name)
with (out/'Mau-Tu-Vung.csv').open(encoding='utf-8-sig', newline='') as f:
    parsed = list(csv.reader(f))
assert parsed[0] == ['English', 'Vietnamese'] and len(parsed) == 13
assert all(len(row) == 2 for row in parsed)
assert len(plain.strip().splitlines()) == 12
print('Created CSV + TXT + guide + ZIP. Verified 12 bilingual entries in both templates.')
