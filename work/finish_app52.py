from pathlib import Path
import json,shutil
root=Path(__file__).resolve().parent.parent; app=root/'outputs/english-app'
p=app/'app/curriculum-data.ts';s=p.read_text(encoding='utf-8')
updates={
"I have two brothers, and we talk almost every weekend.":"I grew up in a small town where most people knew each other.",
"I usually get up at six because I like to have a quiet morning.":"I usually get up around seven, but on weekends I sleep a little later.",
"It looks like rain, so I'm going to bring an umbrella.":"It's been really warm lately, so we've been spending more time outside.",
"I live in a one-bedroom apartment near the library.":"I live in a two-bedroom apartment near the library.",
"Could we meet on Thursday, preferably after lunch?":"What time works best for you if we meet on Thursday?",
"Could we have a table for two near the window, please?":"A table for two near the window, please, if one is available.",
"Could you help me find a quiet café where I can work for an hour?":"Could you say that a little more slowly so I can write down the directions?",
"I have two years of experience in customer support, mainly with online services.":"I have three years of experience in customer support, mainly with online services."
}
for old,new in updates.items():s=s.replace(json.dumps(old),json.dumps(new))
p.write_text(s,encoding='utf-8')
p=app/'app/garden.tsx';s=p.read_text(encoding='utf-8')
s=s.replace("setVoiceName(p.voiceName||'')","setVoiceName(p.voiceLocale==='en-US'?(p.voiceName||''):'')")
s=s.replace('JSON.stringify({rate,voiceName})',"JSON.stringify({rate,voiceName,voiceLocale:'en-US'})")
s=s.replace('Tự động chọn giọng tiếng Anh','Tự động chọn giọng Mỹ (en-US)')
s=s.replace('update(()=>value);', 'update(()=>addCurriculum(value));')
s=s.replace('<div className="lesson-list">{shown.map(l=>', '<div className="actions curriculum-downloads"><a className="btn" href="/curriculum/Tieng-Anh-My-52-Tuan.pdf" download>Sách PDF 125 trang</a><a className="btn" href="/curriculum/Tu-Vung-52-Tuan.zip" download>Từ vựng & bài học để chỉnh sửa</a></div><div className="lesson-list">{shown.map(l=>')
s=s.replace('<label>Nhiệm vụ luyện nói<textarea value={form.task}', '''{(['grammar','pronunciation','usage','twist'] as const).map((key,i)=><label key={key}>{['Ngữ pháp ứng dụng','Phát âm & nghe','Cách dùng theo hoàn cảnh','Tình huống bất ngờ'][i]}<textarea maxLength={2000} value={form[key]||''} onChange={e=>setForm({...form,[key]:e.target.value})}/></label>)}<label>Nhiệm vụ luyện nói<textarea value={form.task}''')
p.write_text(s,encoding='utf-8')
d=app/'public/curriculum';d.mkdir(exist_ok=True)
for name in ['Tieng-Anh-My-52-Tuan.pdf','Tu-Vung-52-Tuan.zip']:shutil.copy2(root/'outputs'/name,d/name)
readme='''ENGLISH GARDEN V1.1 — 52 TUẦN TIẾNG ANH MỸ

MỞ HỌC:
1. Giải nén ZIP vào một thư mục cố định (không chạy trong cửa sổ ZIP).
2. Nhấn đúp MO-APP.cmd. App tự chọn cổng, đợi máy chủ sẵn sàng rồi mở trình duyệt.
3. Vào Bài học > Giáo trình 52 tuần > chọn tuần 1.
4. Lịch học bảy ngày nằm trong Nộp bài. Làm bài, ghi âm, lưu bản ghi và đánh dấu hoàn thành.
5. Giữ trang mở đến khi hiện Đã đồng bộ. Tắt trình duyệt không xóa dữ liệu đã lưu.

CẬP NHẬT APP CŨ:
1. Đợi app cũ lưu xong; đóng các tab app cũ.
2. Trong thư mục bản mới, nhấn CAP-NHAT-V1.1.cmd.
3. Chọn thư mục app cũ có MO-APP.cmd, server.mjs và data.
4. Trình cập nhật dừng đúng máy chủ của thư mục đã chọn, sao lưu data, thay chương trình và mở lại.
5. Nhấn Ctrl+F5 nếu tab còn hiện bản cũ. Giáo trình được bổ sung tự động khi mở app.
Thư mục data không bị xóa. Bài mẫu cũ và bài cá nhân nằm trong bộ Bài cá nhân & bài mẫu cũ.
Các câu trùng không nhập lại vào kho. Nội dung đã sửa, lịch ôn và ghi âm cũ được giữ.

NỘI DUNG:
52 tuần, 312 câu/cụm Anh–Việt, 52 hội thoại, 52 mẫu mở rộng câu.
Ngữ pháp ứng dụng, phát âm Mỹ, cách dùng, flashcards, phản xạ 3 giây, Rapid Fire,
hỏi đáp, điền từ, sửa lỗi, dịch miệng, nhiệm vụ nói và tình huống bất ngờ.
Bốn bài kiểm tra chặng: tuần 13, 26, 39, 52. Học 45–60 phút/ngày và giao tiếp thực tế.
Không bảo đảm mọi người đạt giọng hay trình độ người bản xứ sau một năm.

LƯU TRỮ:
Dữ liệu SQLite và tệp gốc/ghi âm nằm trong data. Giữ nguyên thư mục này khi cập nhật.
JSON giữ nội dung và tiến độ nhưng không chứa tệp ghi âm. Sao lưu đủ bằng cách dừng máy chủ rồi sao chép data.
App dùng riêng trên máy này; chưa đồng bộ máy khác. Không gửi bài tự động cho giáo viên.

NHẬP / CHỈNH SỬA:
PDF, DOCX, DOC, TXT, CSV, TSV và dán văn bản: xem trước, sửa rồi lưu.
PDF scan cần bật OCR, Internet để tải bộ nhận dạng. DOC đặc biệt cần chuyển DOCX.
Sách PDF 125 trang đã có đầy đủ nội dung trong giáo trình; không cần nhập lại PDF này.
Giọng Mỹ mặc định en-US; giọng có sẵn tùy máy. Có thể chọn giọng trong Cài đặt.
Ghi âm cần quyền micro và chỉ được giữ sau khi bấm Lưu bản ghi.

NẾU KHÔNG MỞ:
Cần Node.js 22.13 trở lên (máy hiện tại đã có). Mở MO-APP.cmd trước khi mở 127.0.0.1.
Địa chỉ thực tế nằm trong data/app-url.txt; lỗi nằm trong data/error.log.
Chưa có AI tự dịch, chấm phát âm hay tự đánh giá câu trả lời mở.
'''
(app/'local-app/README.txt').write_text(readme,encoding='utf-8-sig')
# Advertise build identity for diagnosis, and serve book downloads with correct MIME types.
p=app/'local-app/server.mjs';s=p.read_text(encoding='utf-8')
s=s.replace("'.html':'text/html; charset=utf-8'","'.pdf':'application/pdf','.zip':'application/zip','.html':'text/html; charset=utf-8'")
p.write_text(s,encoding='utf-8')
print('Finalized US voice preferences, editable notes, downloads and update instructions.')
