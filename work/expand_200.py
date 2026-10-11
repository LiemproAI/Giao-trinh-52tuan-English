from pathlib import Path
import json, csv, zipfile, html, re, shutil

ROOT=Path(__file__).resolve().parent.parent
app=ROOT/'outputs/english-app'
source=app/'app/curriculum-data.ts'
backup=ROOT/'work/curriculum-v1.json'
if not backup.exists() or backup.read_text(encoding='utf-8').startswith('[]'):
    text=source.read_text(encoding='utf-8')
    backup.write_text(text.split(' = ',1)[1].rstrip().removesuffix(';'),encoding='utf-8')
lessons=json.loads(backup.read_text(encoding='utf-8'))
topics={}
for line in (ROOT/'work/practical_scenarios.txt').read_text(encoding='utf-8').splitlines():
    if line.startswith('@@'):
        n=int(line[2:]); topics[n]=[]
    elif line.strip(): topics[n].append(line.split('|',1))
assert len(topics)==52 and all(len(v)==10 for v in topics.values())

# Reusable functional frames: practice transferring the same skill to concrete situations.
basic=[
 ("I'd like to {a}.","Tôi muốn {v}."),
 ("I need to {a}.","Tôi cần {v}."),
 ("Can I {a}?","Tôi có thể {v} không?"),
 ("Could you help me {a}?","Bạn giúp tôi {v} được không?"),
 ("How can I {a}?","Tôi có thể {v} bằng cách nào?"),
 ("I'm trying to {a}.","Tôi đang cố gắng {v}."),
 ("I don't know how to {a}.","Tôi không biết cách {v}."),
 ("Let me {a} first.","Để tôi {v} trước đã."),
 ("I was going to {a}, but I ran out of time.","Tôi định {v}, nhưng không còn đủ thời gian."),
 ("I haven't had a chance to {a} yet.","Tôi chưa có dịp {v}."),
 ("Do you think I should {a}?","Bạn nghĩ tôi có nên {v} không?"),
 ("Is now a good time for me to {a}?","Bây giờ có phải lúc thích hợp để tôi {v} không?"),
 ("I'll {a} before I leave.","Tôi sẽ {v} trước khi rời đi."),
 ("I forgot to {a}, so I'll do that now.","Tôi quên {v}, nên bây giờ tôi sẽ làm việc đó."),
 ("Would it be possible for me to {a} today?","Hôm nay tôi có thể {v} được không?"),
 ("I'd prefer to {a} in person.","Tôi muốn {v} trực tiếp hơn."),
 ("I wanted to {a}, but I wasn't sure how.","Tôi muốn {v}, nhưng chưa biết làm thế nào."),
 ("I can {a} if you give me a few minutes.","Tôi có thể {v} nếu bạn cho tôi vài phút."),
 ("Before I {a}, could you explain what I should do?","Trước khi tôi {v}, bạn giải thích tôi cần làm gì được không?"),
 ("Thanks for helping me {a}.","Cảm ơn bạn đã giúp tôi {v}."),
]
advanced=[
 ("I'd like to {a}, provided that we have enough time.","Tôi muốn {v}, với điều kiện chúng ta có đủ thời gian."),
 ("I need to {a} before making a final decision.","Tôi cần {v} trước khi đưa ra quyết định cuối cùng."),
 ("Would you mind helping me {a}?","Bạn có phiền giúp tôi {v} không?"),
 ("Could you explain the best way to {a}?","Bạn giải thích cách tốt nhất để {v} được không?"),
 ("What would you recommend if I wanted to {a}?","Bạn sẽ gợi ý gì nếu tôi muốn {v}?"),
 ("I'm trying to {a} without overlooking any important details.","Tôi đang cố {v} mà không bỏ sót chi tiết quan trọng nào."),
 ("I'm not sure how to {a}, so I'd appreciate some guidance.","Tôi chưa chắc nên {v} thế nào, nên rất mong được hướng dẫn."),
 ("Let me {a} first, and then we can discuss the next step.","Để tôi {v} trước, rồi chúng ta có thể trao đổi bước tiếp theo."),
 ("I intended to {a}, but something unexpected came up.","Tôi định {v}, nhưng có việc bất ngờ xảy ra."),
 ("I haven't been able to {a} yet, despite making several attempts.","Tôi vẫn chưa thể {v}, dù đã thử vài lần."),
 ("Do you think it would be more effective for me to {a} in person?","Bạn nghĩ tôi {v} trực tiếp thì có hiệu quả hơn không?"),
 ("If I were in your position, I'd {a} before moving forward.","Nếu ở vị trí của bạn, tôi sẽ {v} trước khi tiếp tục."),
 ("I'll {a} as soon as I have the information I need.","Tôi sẽ {v} ngay khi có thông tin cần thiết."),
 ("Looking back, I should have taken the time to {a}.","Nhìn lại, lẽ ra tôi nên dành thời gian để {v}."),
 ("Is there any reason why I shouldn't {a} at this stage?","Có lý do nào khiến tôi không nên {v} ở giai đoạn này không?"),
 ("I'd rather {a} now than deal with a misunderstanding later.","Tôi muốn {v} ngay hơn là phải xử lý hiểu nhầm sau này."),
 ("Although it may take longer, I'd still prefer to {a} properly.","Dù có thể mất thêm thời gian, tôi vẫn muốn {v} cho đúng."),
 ("Unless there is a better alternative, I plan to {a}.","Trừ khi có phương án tốt hơn, tôi dự định {v}."),
 ("The main reason I want to {a} is to avoid unnecessary confusion.","Lý do chính tôi muốn {v} là để tránh những nhầm lẫn không cần thiết."),
 ("Once I've had a chance to {a}, I'll be in a better position to respond.","Sau khi có dịp {v}, tôi sẽ có đủ cơ sở hơn để phản hồi."),
]
plans=[
 'Câu 001–040: hiểu ý, nghe từng câu, nhại lại và đổi thông tin thành của bạn. Chọn 10 câu chủ lực.',
 'Câu 041–080: nghe khi che chữ, ghi lại ý chính, chép chính tả 10 câu; kiểm tra với bản gốc.',
 'Câu 081–120: nhìn nghĩa Việt rồi nói Anh. Không cần giống từng chữ nếu ý đúng và ngữ pháp phù hợp.',
 'Câu 121–160: đóng vai người cần hỗ trợ và người trả lời; hỏi thêm, trả lời tự do và xác nhận thông tin.',
 'Câu 161–200: đọc, tìm mục đích của người nói, phân biệt yêu cầu/gợi ý/giả định; viết một tin nhắn áp dụng.',
 'Thực hiện một tình huống thật hoặc mô phỏng mới. Trò chuyện với người khác 15–30 phút, thu âm và xin góp ý.',
 'Kiểm tra không nhìn bài; ôn 20 câu khó và câu của các tuần cách 1, 3, 6 tuần. Ghi lỗi và luyện lại.',
]
out=ROOT/'outputs/Giao-Trinh-52-Tuan-200-Cau';out.mkdir(exist_ok=True)
for l in lessons:
    n=l['week'];level='A1–A2' if n<=13 else 'A2–B1' if n<=26 else 'B1' if n<=39 else 'B1–B2'
    frames=basic if n<=13 else basic[:10]+advanced[10:] if n<=26 else basic[:4]+advanced[4:] if n<=39 else advanced
    phrases=[]
    for i,(a,v) in enumerate(topics[n]):
        group=[]
        if i==0:group.extend(l['phrases'])
        for en,vi in frames:
            if len(group)==20:break
            group.append({'en':en.format(a=a,v=v),'vi':vi.format(a=a,v=v)})
        phrases.extend(group)
    assert len(phrases)==200 and len({p['en'] for p in phrases})==200
    l['phrases']=phrases;l['curriculumVersion']=2
    l['practiceGroups']=[v for a,v in topics[n]]
    l['dailyPlan']=plans.copy()
    l['description']+=' | 200 câu luyện theo mẫu trong 10 tình huống · Chặng '+level
    l['usage']+='\nCâu mở rộng luyện cùng một chức năng giao tiếp qua nhiều tình huống; chọn cách nói phù hợp, không dùng mọi mẫu trong một cuộc trò chuyện. Từ “I” là người đang thực hiện hành động; vai người nghe thay đổi theo ngữ cảnh.'
    goal='Nói 2 phút, đáp lại 5 câu hỏi đơn giản; viết tin nhắn 60–80 từ.' if n<=13 else 'Nói 3 phút, trao đổi 8 phút có câu hỏi tiếp nối; viết email 100–140 từ.' if n<=26 else 'Nói 4 phút, xử lý một hiểu nhầm và đề xuất cách giải quyết; viết 140–180 từ.' if n<=39 else 'Nói 4–5 phút có quan điểm, lý do, ví dụ và ý phản biện; trao đổi 12–15 phút; viết 180–220 từ.'
    l['task']+='\nMục tiêu chặng '+level+': '+goal+'\nĐọc: chọn 20 câu, xác định ý chính và mức độ lịch sự. Nghe: che chữ, nghe 10 câu và hội thoại, ghi 5 ý chính và 5 chi tiết. Viết: gửi tin nhắn/email gắn với một tình huống dưới đây; sửa sau góp ý.\nKhông chỉ học thuộc: thay người, thời gian, địa điểm; hỏi thêm và phản hồi điều chưa chuẩn bị.'
    l['twist']+='\nTình huống chuyển giao: chọn ngẫu nhiên một trong 10 nhóm, thêm trở ngại về thời gian/chi phí/hiểu nhầm. Người đối thoại đưa một câu hỏi mới; bạn phải làm rõ, đề xuất và xác nhận giải pháp.'
    l['qa'] += [{'en':'What would you say if you needed to '+a+'?', 'vi':'Ví dụ: '+phrases[i*20]['en']+' Sau đó nêu thông tin cụ thể và hỏi thêm một câu.'} for i,(a,v) in enumerate(topics[n])]
    # More meaningful application practice, using existing answer machinery.
    l['exercises'] += [{'question':re.sub(r"^(I'd|I|Can|Could|How|I'm|Let|Would|What|Do|If|I'll|Looking|Is|Although|Unless|The|Once)\b",'____',p['en']), 'answer':p['en'].split()[0]} for p in phrases[6:26]]
    l['translations']=phrases[::10]
    l['dailyPlan'][5]+=' Chủ đề tự chọn: '+topics[n][min(9,n%10)][1]+'.'
    if n in (13,26,39,52):
        l['task']+='\nKIỂM TRA CHẶNG: người khác chọn tình huống chưa chuẩn bị; nghe một đoạn mới phù hợp chặng, đọc một bài mới, nói và viết theo yêu cầu. Nhờ giáo viên đánh giá theo CEFR; app chỉ lưu bài, không cấp chứng chỉ hoặc tự xác nhận trình độ.'
    csvpath=out/f'Tuan-{n:02}-200-Cau.csv'
    with csvpath.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['English','Vietnamese']);writer.writerows((p['en'],p['vi']) for p in phrases)
    (out/f'Tuan-{n:02}-200-Cau.txt').write_text('\n'.join(p['en']+' | '+p['vi'] for p in phrases)+'\n',encoding='utf-8-sig')
source.write_text('import type {Lesson} from "./model";\nexport const curriculumLessons:Lesson[] = '+json.dumps(lessons,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(ROOT/'work/curriculum-v2.json').write_text(json.dumps(lessons,ensure_ascii=False),encoding='utf-8')

guide='''GIÁO TRÌNH 52 TUẦN × 200 CÂU — HƯỚNG TỚI B2
10.400 câu Anh–Việt. Mỗi tuần: 10 nhóm, mỗi nhóm 20 câu.
Giữ sáu câu gốc ở đầu nhóm 1. Các câu mới là bài tập chuyển mẫu giao tiếp sang 10 hành động thực tế; có sự lặp lại cấu trúc giữa các nhóm và tuần. Đây không phải 10.400 mẫu ngữ pháp độc lập.
Tuần 1–13: nền tảng A1–A2; 14–26: A2–B1; 27–39: B1; 40–52: B1–B2.
Các nhãn trên là mục tiêu thiết kế, không phải chứng nhận độ khó hay bảo đảm đầu ra.
Học 40 câu/ngày trong 5 ngày; ngày 6 thực hành, ngày 7 ôn và kiểm tra. Chọn 10–20 câu chủ lực, còn lại dùng để luyện thay đổi tình huống. Dành 60–90 phút/ngày và nhiều buổi trò chuyện có phản hồi.
Nghe nhại: nghe câu ở 0.9×, rồi 1.0×; lặp lại trọng âm, không đọc từng từ rời.
Nghe thật: mỗi tuần nghe ít nhất hai đoạn hội thoại/phỏng vấn mới; nghe ý chính rồi chi tiết, cuối cùng kiểm tra bản chép. Âm thanh TTS không thay thế hoàn toàn người nói thật.
Đọc thật: mỗi tuần đọc hai bài mới (email, hướng dẫn, tin tức, bài ý kiến); tóm tắt và phân biệt sự kiện với quan điểm. Tuần cuối tăng lên 400–700 từ/bài.
Nói: đóng vai, hỏi thêm và đổi điều kiện. Viết: tin nhắn/email rồi đoạn lập luận; nhờ người có năng lực sửa.
Các ví dụ về sức khỏe, tiền bạc và hợp đồng chỉ luyện ngôn ngữ, không đưa phác đồ điều trị, lời khuyên đầu tư hay kết luận pháp lý.

KIỂM TRA TUẦN 13 / 26 / 39 / 52
Không dùng câu đã luyện làm toàn bộ đề thi. Nhờ giáo viên chọn tài liệu mới tương đương chặng.
Tuần 13: nghe hội thoại chậm về đời sống, đọc 150 từ, đóng vai 3 phút, viết 60–80 từ.
Tuần 26: nghe hội thoại 2–3 phút, đọc 250 từ, xử lý vấn đề khi đi lại/công việc, viết 100–140 từ.
Tuần 39: nghe hội thoại 4 phút, đọc 350–450 từ, trao đổi có giải pháp và hỏi tiếp, viết 140–180 từ.
Tuần 52: nghe 5–7 phút ở tốc độ tự nhiên, đọc 500–700 từ về chủ đề cụ thể hoặc trừu tượng, trình bày 4–5 phút và trao đổi 12–15 phút, viết 180–220 từ nêu hai phía và kết luận.
Yêu cầu nói cuối khóa: nêu quan điểm, có lý do và ví dụ; trả lời phản biện; làm rõ điều chưa hiểu; nối ý mạch lạc; lỗi không làm người nghe khó hiểu kéo dài.
Nhờ giáo viên đánh giá phạm vi ngôn ngữ, độ chính xác, độ trôi chảy, tương tác và mạch lạc theo CEFR. Theo dõi riêng nghe/đọc/viết, không dùng điểm điền từ để kết luận B2.
Đây là kế hoạch hướng tới B2. Đạt B2 cần năng lực thực tế và đánh giá độc lập; app không thể hứa rằng chỉ học hết 200 câu mỗi tuần là đạt.
Nguồn tiêu chí: https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale
https://www.coe.int/en/web/common-european-framework-reference-languages/table-3-cefr-3.3-common-reference-levels-qualitative-aspects-of-spoken-language-use

CÁCH DÙNG
App đã chứa nội dung: tải lại trang, vào bài học, chọn nhóm 20 câu.
CSV/TXT dùng để học ngoài app hoặc nhập vào Kho từ vựng/Bài học mới; không cần nhập lại nếu app đã cập nhật.
Các sửa đổi, tiến độ và bài cá nhân cũ được giữ. Dấu hoàn thành cũ không đồng nghĩa bạn đã luyện hết 200 câu mới.
'''
(out/'HUONG-DAN-B2.txt').write_text(guide,encoding='utf-8-sig')
page=['<!doctype html><html lang="vi"><meta charset="utf-8"><title>52 tuần × 200 câu — hướng tới B2</title><style>body{font:18px/1.65 Georgia,serif;max-width:1100px;margin:35px auto;padding:20px;color:#173b2c}table{border-collapse:collapse;width:100%}td{padding:10px;border-bottom:1px solid #ddd}td:first-child{width:45%}nav{display:flex;flex-wrap:wrap;gap:12px}details{margin:24px 0}pre{white-space:pre-wrap;font:inherit}@media print{details{display:block}nav{display:none}}</style><h1>52 tuần × 200 câu: hướng tới B2</h1><details open><summary>Hướng dẫn học và đánh giá</summary><pre>'+html.escape(guide)+'</pre></details><nav>']
page += [f'<a href="#week-{l["week"]}">Tuần {l["week"]}</a>' for l in lessons];page+=['</nav>']
for l in lessons:
    n=l['week'];page += [f'<section id="week-{n}"><h2>Tuần {n}: {html.escape(l["title"])}</h2><p>{html.escape(l["task"]).replace(chr(10),"<br>")}</p>']
    for i,(a,v) in enumerate(topics[n]):
        page += [f'<details open><summary>Nhóm {i+1}: {html.escape(v)}</summary><table>']
        for j,p in enumerate(l['phrases'][i*20:(i+1)*20],i*20+1):page += [f'<tr><td>{j:03}. {html.escape(p["en"])}</td><td>{html.escape(p["vi"])}</td></tr>']
        page+=['</table></details>']
    page+=['</section>']
htmlpath=ROOT/'outputs/Tieng-Anh-52-Tuan-10400-Cau.html';htmlpath.write_text('\n'.join(page),encoding='utf-8')
zipath=ROOT/'outputs/Giao-Trinh-52-Tuan-200-Cau.zip'
with zipfile.ZipFile(zipath,'w',zipfile.ZIP_DEFLATED) as z:
    for p in out.iterdir():z.write(p,p.name)
for public in [ROOT/'outputs/public/curriculum',app/'local-app/public/curriculum']:
    public.mkdir(exist_ok=True,parents=True)
    shutil.copy2(zipath,public/zipath.name);shutil.copy2(htmlpath,public/htmlpath.name)
print(json.dumps({'weeks':len(lessons),'sentences':sum(len(l['phrases']) for l in lessons),'fileBytes':source.stat().st_size,'archive':str(zipath)},ensure_ascii=False))
