from pathlib import Path
import re, json, csv, io, zipfile, html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
weeks=[]
for fn in ['curriculum.txt','curriculum-2.txt','curriculum-3.txt','curriculum-4.txt']:
    for line in (ROOT/'work'/fn).read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        if line.startswith('@@ '):
            n,en,vi=line[3:].split('|'); w=dict(n=int(n),en=en,vi=vi,P=[],D=[],Q=[]); weeks.append(w)
        else:
            key,val=line.split(' ',1)
            if key in ('P','D','Q'): w[key].append(val.split('|',1))
            elif key=='FIX': w[key]=val.split('|',1)
            else: w[key]=val
assert [w['n'] for w in weeks]==list(range(1,53))
for w in weeks:
    assert all(k in w for k in ['GOAL','GRAMMAR','SOUND','REGISTER','FIX','TASK','TWIST'])
    assert len(w['P'])==len(w['D'])==6 and len(w['Q'])==2
    w['ex']=[]
    for en,vi in w['P'][:3]:
        tokens=list(re.finditer(r'[A-Za-z]+(?:\x27[A-Za-z]+)?',en))
        candidates=[t for t in tokens if len(t.group())>=4 and "'" not in t.group()]
        t=candidates[-1] if candidates else tokens[-1]
        w['ex'].append([en[:t.start()]+'______'+en[t.end():],t.group()])

for nm,fn in [('Regular','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(nm,'C:/Windows/Fonts/'+fn))
NAVY=HexColor('#12382c'); GOLD=HexColor('#b47519'); GRAY=HexColor('#53645e'); LINE=HexColor('#d7e3dc')
W,H=595.28,841.89; M=43; CONTENT=W-2*M
pdf=OUT/'Tieng-Anh-My-52-Tuan.pdf'
c=canvas.Canvas(str(pdf),pagesize=(W,H))
c.setTitle('Tiếng Anh Mỹ — 52 tuần giao tiếp'); c.setAuthor('Giáo trình tự học Anh–Việt')
page=0; y=0; page_notes=[]
def new_page(label):
    global page,y
    if page: c.showPage()
    page+=1; y=H-61
    c.setFillColor(NAVY); c.rect(0,H-34,W,34,fill=1,stroke=0)
    c.setFont('Bold',8); c.setFillColor(white); c.drawString(M,H-22,'TIẾNG ANH MỸ • 52 TUẦN GIAO TIẾP')
    c.setFont('Regular',8); c.drawRightString(W-M,H-22,label)
    c.setStrokeColor(LINE); c.line(M,35,W-M,35)
    c.setFillColor(GRAY); c.setFont('Regular',8); c.drawString(M,22,'Nghe • Nói • Tương tác • Ôn tập')
    c.drawRightString(W-M,22,str(page)); page_notes.append(label)
def p(text,size=10.4,bold=False,color=NAVY,gap=6,indent=0):
    global y
    st=ParagraphStyle('x',fontName='Bold' if bold else 'Regular',fontSize=size,leading=size*1.32,textColor=color)
    pp=Paragraph(html.escape(text),st); _,height=pp.wrap(CONTENT-indent,1000)
    if y-height < 48: raise RuntimeError(f'Overflow page {page} {page_notes[-1]} at {text[:45]} y={y} h={height}')
    pp.drawOn(c,M+indent,y-height); y-=height+gap
def title(t,sub=None):
    p(t,21,True,gap=9)
    if sub:p(sub,11,color=GOLD,gap=12)
def section(t):p(t,11.3,True,color=GOLD,gap=6)
def rule():
    global y
    c.setStrokeColor(LINE); c.line(M,y,W-M,y); y-=10

new_page('Bắt đầu')
p('52 TUẦN',35,True,gap=2); p('GIAO TIẾP TIẾNG ANH MỸ',24,True,gap=18)
p('Giáo trình tự học Anh–Việt • Đời sống • Công việc • Giao tiếp xã hội',12,color=GOLD,gap=20)
p('Mục tiêu: nói rõ, nghe tốt hơn, duy trì cuộc trò chuyện và xử lý tình huống thực tế. Học cách diễn đạt tự nhiên theo tiếng Anh Mỹ, với sự linh hoạt và lịch sự.',13,gap=18)
section('Bạn sẽ học những gì?')
for t in ['52 chủ đề có mục tiêu cụ thể, 312 câu/cụm Anh–Việt và 52 hội thoại mẫu (312 lượt nói).','Mỗi tuần: mẫu diễn đạt, ngữ pháp ứng dụng, phát âm, cách dùng theo hoàn cảnh, câu hỏi hiểu bài, bài tập và tình huống bất ngờ.','Bốn bài kiểm tra chặng ở tuần 13, 26, 39 và 52; đáp án ở cuối sách.','Bản HTML đi kèm có nút nghe, bài tập và đánh dấu hoàn thành. Bộ CSV cho phép bổ sung câu vào kho từ vựng của app.']:p('• '+t,11,gap=8)
rule(); section('Kỳ vọng thực tế')
p('Không khóa học nào bảo đảm sau một năm mọi người đều nói như người bản xứ. Kết quả phụ thuộc điểm xuất phát, thời lượng, chất lượng luyện tập và phản hồi. Tiếng Anh Mỹ có nhiều giọng; mục tiêu chính của sách là giao tiếp dễ hiểu và tự nhiên, không xóa bản sắc giọng nói của bạn.',11,gap=10)
p('Phù hợp nhất với người đã biết câu cơ bản. Nếu mới bắt đầu hoàn toàn, dành thêm thời gian cho tuần 1–6, bảng chữ cái, số và động từ thường dùng. Nếu đã khá, tăng phần nói tự phát và tài liệu nghe thực tế.',11)
p('Nội dung tình huống, tên, địa chỉ và số liệu là ví dụ học ngôn ngữ. Các tuần sức khỏe, ngân hàng và nhà ở không thay cho tư vấn chuyên môn.',9.5,color=GRAY)

new_page('Cách học')
title('Một tuần học như thế nào?','45–60 phút mỗi ngày, 6 ngày; ngày 7 ôn nhẹ hoặc nghỉ')
for h,t in [('Ngày 1 · Hiểu và cá nhân hóa','Đọc mục tiêu, sáu câu Anh–Việt và ghi chú. Thay tên, nghề, nơi ở hoặc thời gian để câu đúng với bạn. Nói từng câu 5 lần có thay chi tiết.'),('Ngày 2 · Nghe và nhại có kiểm soát','Nghe câu và hội thoại trong bản HTML. Nghe chậm nếu cần, sau đó tốc độ thường. Luyện từng cụm, chú ý trọng âm. Nhại khoảng 5–10 giây; hiểu ý trước khi lặp.'),('Ngày 3 · Nhớ chủ động','Che câu Anh, nhìn Việt rồi nói Anh. Làm ba câu điền từ, sửa lỗi và dịch hai câu. Kiểm tra đáp án; ghi lý do sai, không chỉ ghi điểm.'),('Ngày 4 · Đối thoại','Đóng cả vai A và B trước; sau đó đổi vai với bạn học. Dùng câu hỏi hiểu bài làm khởi động và hỏi thêm ít nhất ba câu chưa có trong mẫu.'),('Ngày 5 · Nhiệm vụ và biến thể','Thực hiện TASK rồi TWIST của tuần. Chỉ nhìn 5 từ khóa, không đọc kịch bản. Nếu không có bạn học, ghi âm hai lượt đối thoại với khoảng dừng.'),('Ngày 6 · Giao tiếp thật và phản hồi','Nói 10–20 phút với bạn học, giáo viên hoặc người đồng ý trò chuyện. Xin sửa một vấn đề về độ rõ và một vấn đề về cách diễn đạt. Nếu chưa có đối tác, tự thu âm rồi nghe lại.'),('Ngày 7 · Ôn cách quãng','Ôn câu của tuần này và các tuần cách 1, 3, 6 tuần. Chọn 10 câu ngẫu nhiên, nói không nhìn đáp án. Nghỉ nếu cần; không bỏ phần ôn dài hạn.')]:
    section(h);p(t,10.5,gap=10)
rule();p('Khung 50 phút gợi ý: 10 phút ôn cũ + 10 phút nghe + 10 phút luyện câu + 15 phút nói/đối thoại + 5 phút ghi lỗi. Cần thêm tương tác thực tế để phát triển khả năng ứng biến.',10.5)

new_page('Đo tiến bộ')
title('Đo tiến bộ bằng việc bạn làm được')
section('Ghi âm mốc đầu và các chặng')
p('Trước tuần 1, thu 60–90 giây tự giới thiệu. Giữ lại bản thu. Sau tuần 13, 26, 39 và 52, thu bài kiểm tra chặng mà không đọc kịch bản. So sánh với chính bạn, không chỉ với tốc độ người bản xứ.')
section('Thang tự đánh giá 0–3 cho mỗi tiêu chí')
for t in ['Hoàn thành nhiệm vụ: 0 chưa làm được; 1 cần gợi ý liên tục; 2 làm được với ít gợi ý; 3 tự làm và xử lý thay đổi.','Độ dễ hiểu: 0 thường khó hiểu; 1 cần nhắc lại nhiều; 2 đa số rõ; 3 rõ xuyên suốt, có trọng âm giúp người nghe.','Tương tác: 0 chưa phản hồi; 1 chủ yếu trả lời ngắn; 2 hỏi tiếp nối và nhường lượt; 3 phát triển đối thoại linh hoạt.','Sửa hiểu nhầm: 0 dừng; 1 cần hỗ trợ; 2 hỏi lại hoặc nói lại được; 3 xác nhận và tiếp tục tự nhiên.','Cách diễn đạt: 0 từ rời; 1 câu quen thuộc; 2 nhiều mẫu phù hợp; 3 chọn cách nói theo người nghe và hoàn cảnh.']:p('• '+t,10.7,gap=9)
p('Tổng 0–15 là công cụ theo dõi riêng, không phải điểm thi CEFR hay chứng chỉ. Khi một tiêu chí dưới 2, lặp nhiệm vụ với tình huống mới trước khi tăng độ khó.',10.5,gap=12)
section('Nhật ký lỗi ngắn')
p('Ngày / Tình huống / Tôi đã nói / Cách nói rõ hơn / Lý do / Ngày ôn lại. Mỗi buổi chỉ chọn 1–2 lỗi có ích. Giữ thông tin cá nhân nhạy cảm ngoài nhật ký chia sẻ.')
section('Nghe theo tiếng Anh Mỹ')
p('Bản HTML ưu tiên giọng en-US có sẵn trên thiết bị. Giọng tổng hợp giúp luyện câu, nhưng không thay được tiếng nói thật. Nghe thêm nhiều người Mỹ, các vùng và nhịp khác nhau; dùng phụ đề khi cần rồi nghe lại không phụ đề.')

new_page('Tài liệu bổ trợ và sử dụng')
title('Học thêm và dùng bộ tài liệu')
section('Nguồn nghe bổ trợ')
p('VOA Learning English — Let’s Learn English Level 1: khóa video cho người mới học, dùng bổ trợ nghe và kiến thức cơ bản. Giáo trình trong sách này được viết riêng, không phải bản sao khóa VOA.')
p('https://learningenglish.voanews.com/p/5644.html',9.7,color=GRAY)
p('U.S. Department of State — Everyday Conversations: hội thoại và âm thanh cho các tình huống đời thường. Chọn đoạn liên quan chủ đề tuần, nghe rồi thử thay dữ kiện.')
p('https://americanenglish.state.gov/resources/everyday-conversations-learning-american-english',9.7,color=GRAY)
p('Council of Europe — CEFR level descriptions: mô tả khả năng làm được ở từng mức. Có thể tham khảo để đặt mục tiêu, không dùng số tuần học để tự khẳng định đạt mức.')
p('https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions',9.7,color=GRAY)
section('Bản học trên trình duyệt')
p('Mở Tieng-Anh-My-52-Tuan.html bằng Edge hoặc Chrome. Chọn tuần, dùng nút nghe, che nghĩa Việt, làm bài và xem đáp án. Giọng và phát âm phụ thuộc thiết bị; một số giọng cần mạng. Tiến độ lưu trong trình duyệt, không đồng bộ giữa máy.')
section('Nhập vào app và cập nhật')
p('Giải nén Tu-Vung-52-Tuan.zip. Chọn một CSV theo tuần trong chức năng nhập từ vựng của app; hai cột là English và Vietnamese. Có tệp tổng 312 câu, chỉ nhập tệp tổng hoặc từng tuần để tránh trùng. Xem trước dữ liệu rồi bổ sung vào bộ đang học.')
p('Các TXT theo tuần chứa toàn bộ nội dung, có thể sửa bằng trình soạn thảo và nhập dạng văn bản nếu app hỗ trợ. Giữ một bản sao ngoài app trước khi sửa hoặc cập nhật. Bộ tài liệu không tự thay đổi dữ liệu bạn đã có.')
section('Cách dùng đáp án')
p('Điền từ và sửa lỗi có đáp án mục tiêu. Dịch và nói có thể có nhiều cách đúng; câu mẫu chỉ là một lựa chọn. Khi tự chấm, xét ý, ngữ pháp và mức lịch sự, không chỉ so từng chữ.')

for start in [0,13,26,39]:
    new_page('Lộ trình'); title(f'Lộ trình tuần {start+1}–{start+13}')
    for w in weeks[start:start+13]:
        link_top=y
        p(f"{w['n']:02d} · {w['en']}  ·  trang {9+2*(w['n']-1)}",12,True,gap=3)
        p(w['vi'],10.5,color=GRAY,gap=12)
        c.linkRect('',f"week{w['n']}",(M,y,W-M,link_top),relative=0,thickness=0)

for w in weeks:
    n=w['n']; new_page(f'Tuần {n:02d} • Mẫu diễn đạt')
    c.bookmarkPage(f'week{n}');c.addOutlineEntry(f"Tuần {n:02d} · {w['en']}",f'week{n}',level=0,closed=False)
    title(f"Tuần {n:02d} · {w['en']}",w['vi'])
    section('Mục tiêu');p(w['GOAL'],10.7,gap=9)
    section('Sáu câu/cụm để dùng ngay')
    for i,(en,vi) in enumerate(w['P'],1):
        p(f'{i}. {en}',11.4,True,gap=2)
        p(vi,10.1,color=GRAY,gap=9,indent=14)
    rule()
    for k,h in [('GRAMMAR','Mẫu ngữ pháp trong giao tiếp'),('SOUND','Phát âm và nghe theo tiếng Anh Mỹ'),('REGISTER','Cách dùng và hoàn cảnh')]:
        section(h);p(w[k],10.5,gap=10)
    p('Cá nhân hóa: chọn ba câu và thay ít nhất hai chi tiết trong mỗi câu. Nói lại không nhìn sách.',10,color=GOLD)
    new_page(f'Tuần {n:02d} • Đối thoại và luyện tập')
    title('Đối thoại và luyện tập',f"Tuần {n:02d} · {w['vi']}")
    for i,(en,vi) in enumerate(w['D']):
        p(('A' if i%2==0 else 'B')+': '+en,10.4,True,gap=1)
        p(vi,9.6,color=GRAY,gap=5,indent=15)
    rule();section('Hiểu bài · trả lời bằng tiếng Anh')
    for i,(q,a) in enumerate(w['Q'],1):p(f'{i}. {q}',10,gap=3)
    section('Luyện nhớ · làm trước khi xem đáp án')
    for i,(q,a) in enumerate(w['ex'],1):p(f'{i}. {q}',10,gap=3)
    p('4. Sửa lỗi: '+w['FIX'][0],10,gap=3)
    p('5–6. Nói bằng tiếng Anh: '+w['P'][3][1]+' / '+w['P'][4][1],10,gap=7)
    section('Nói tự phát · không đọc kịch bản')
    p(w['TASK'],10,gap=5);p('Đổi tình huống: '+w['TWIST'],10,gap=7)
    p('Tự kiểm tra: hoàn thành nhiệm vụ / dễ hiểu / hỏi tiếp nối / sửa hiểu nhầm / phù hợp hoàn cảnh. Chấm mỗi tiêu chí 0–3 và chọn một điều luyện lại.',9.5,color=GRAY,gap=3)
    p('Ôn tuần này sau 1, 3 và 6 tuần. Đáp án ở phần cuối sách.',9.5,color=GOLD)

for start in range(0,52,4):
    new_page('Đáp án');title(f'Đáp án · tuần {start+1}–{min(start+4,52)}')
    for w in weeks[start:start+4]:
        section(f"Tuần {w['n']:02d} · {w['en']}")
        for i,(q,a) in enumerate(w['Q'],1):p(f'Hiểu bài {i}: {a}',9.8,gap=3)
        p('Điền từ 1–3: '+' / '.join(x[1] for x in w['ex']),9.8,gap=3)
        p('Sửa lỗi 4: '+w['FIX'][1],9.8,gap=3)
        p('Dịch 5: '+w['P'][3][0],9.8,gap=3)
        p('Dịch 6: '+w['P'][4][0],9.8,gap=9)
    p('Dịch có thể có cách đúng khác. Với bài nói, dùng thang 0–3 ở đầu sách và xin phản hồi thực tế.',9.5,color=GRAY)
c.save()

data=json.dumps(weeks,ensure_ascii=False).replace('<','\\u003c')
htmlfile=OUT/'Tieng-Anh-My-52-Tuan.html'
template=r'''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>52 tuần giao tiếp tiếng Anh Mỹ</title>
<style>:root{--g:#12382c;--a:#edb24a;--line:#d8e4dd}*{box-sizing:border-box}body{margin:0;background:#f6f8f4;color:#18392f;font:16px/1.6 system-ui,sans-serif}header{background:var(--g);color:white;padding:28px max(20px,calc((100% - 1060px)/2))}h1{font:700 clamp(28px,5vw,44px)/1.2 Georgia,serif;margin:8px 0}header p{max-width:800px}main{max-width:1100px;margin:24px auto;padding:0 20px;display:grid;grid-template-columns:250px 1fr;gap:24px}aside{align-self:start;position:sticky;top:10px;max-height:90vh;overflow:auto;background:white;border:1px solid var(--line);border-radius:12px;padding:15px}article{min-width:0}section,.card{background:white;padding:22px;border:1px solid var(--line);border-radius:12px;margin-bottom:18px}h2,h3{line-height:1.3}h2{font-family:Georgia,serif;font-size:30px}h3{margin-top:0}button,input,select,textarea{font:inherit}button{border:1px solid var(--line);border-radius:8px;background:#e8f1eb;color:var(--g);cursor:pointer;padding:8px 12px}button:hover{background:#d5e7da}button:focus-visible{outline:3px solid #edb24a;outline-offset:2px}.gold{background:var(--a)}.nav{display:block;text-align:left;width:100%;margin:7px 0;font-size:14px}.nav.active{background:var(--g);color:white}.vi{color:#607269;margin:2px 0 8px}.hide-vi .vi{display:none}.row{display:flex;gap:12px;justify-content:space-between;align-items:start;border-bottom:1px solid var(--line);padding:12px 0}.row:last-child{border-bottom:0}.row strong{display:block}.small{font-size:13px}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.dialogue{padding:11px 15px;border-left:3px solid #b47519;background:#f7f9f6;margin-bottom:10px}input[type=search],input.answer,textarea{width:100%;border:1px solid var(--line);padding:10px;border-radius:7px}input.answer{margin:6px 0 12px}textarea{min-height:110px}summary{cursor:pointer;font-weight:650}a{color:#1e6750}header a{color:#ffe0a7}.result{white-space:pre-line;font-weight:650}.badge{font-size:13px;color:#7b4a00;background:#ffeac5;border-radius:20px;padding:4px 12px}footer{padding:20px;text-align:center;color:#607269}@media(max-width:760px){main{display:block}aside{position:static;max-height:220px;margin-bottom:20px}.controls select{max-width:100%}section{padding:18px}}@media print{header,aside,.controls,button{display:none}main{display:block;margin:0}section{break-inside:avoid}body{background:white}}</style>
<header><span class="badge">GIÁO TRÌNH ANH–VIỆT</span><h1>52 tuần giao tiếp tiếng Anh Mỹ</h1><p>312 câu/cụm • 52 hội thoại • luyện nói và ôn theo chặng. Mục tiêu là giao tiếp tự nhiên, dễ hiểu; không bảo đảm đạt trình độ người bản xứ sau một năm.</p><div class="controls"><label>Giọng Mỹ <select id="voice" aria-label="Chọn giọng Mỹ"><option>Đang tìm giọng…</option></select></label><label>Tốc độ <select id="rate"><option value="0.8">0.8×</option><option value="1" selected>1×</option><option value="1.1">1.1×</option></select></label><button id="stop">Dừng nghe</button><button id="toggle">Ẩn nghĩa Việt</button></div><p id="voiceStatus" class="small" role="status"></p></header>
<main><aside><label for="search">Tìm tuần / chủ đề</label><input id="search" type="search" placeholder="Ví dụ: công việc"><p id="progress" class="small"></p><nav id="weeks" aria-label="Danh sách tuần"></nav></aside><article><details class="card"><summary>Cách học và cách lưu tiến độ</summary><p>Mỗi ngày 45–60 phút: 10 phút ôn, 10 phút nghe, 10 phút luyện câu, 15 phút nói, 5 phút ghi lỗi.</p><ol><li>Ngày 1: hiểu sáu câu, thay chi tiết thành thông tin của bạn.</li><li>Ngày 2: nghe, nhại theo cụm, luyện trọng âm.</li><li>Ngày 3: che câu Anh, nhìn Việt nói Anh; làm bài.</li><li>Ngày 4: đổi vai đối thoại, hỏi thêm ba câu.</li><li>Ngày 5: nhiệm vụ nói và tình huống bất ngờ.</li><li>Ngày 6: trò chuyện thật, xin góp ý về độ rõ và cách dùng.</li><li>Ngày 7: ôn tuần cách 1, 3, 6 tuần hoặc nghỉ.</li></ol><p>Chấm mỗi tiêu chí 0–3: hoàn thành nhiệm vụ, dễ hiểu, tương tác, sửa hiểu nhầm, cách diễn đạt. Đây là thang theo dõi cá nhân, không phải chứng chỉ. Tuần 13, 26, 39, 52 có bài kiểm tra chặng.</p><p>Tiến độ và ghi chú lưu trong trình duyệt này khi trình duyệt cho phép. Hãy xuất bản sao để giữ lâu dài; không tự đồng bộ sang app hay máy khác. Giọng tổng hợp phụ thuộc thiết bị, có thể cần mạng.</p><div class="controls"><button id="export">Xuất tiến độ</button><label>Khôi phục <input id="restore" type="file" accept=".json,application/json"></label></div><p id="storageStatus" role="status"></p><p>Nghe bổ trợ: <a href="https://learningenglish.voanews.com/p/5644.html" target="_blank" rel="noopener">VOA Learning English</a> và <a href="https://americanenglish.state.gov/resources/everyday-conversations-learning-american-english" target="_blank" rel="noopener">Everyday Conversations</a>. Tham khảo <a href="https://www.coe.int/en/web/common-european-framework-reference-languages/level-descriptions" target="_blank" rel="noopener">mô tả CEFR</a> để đặt mục tiêu. Giáo trình này được viết riêng.</p></details><div id="content"></div></article></main><footer>Luyện đều, ôn cách quãng, tăng tương tác thực tế. Giữ lại bản thu để thấy tiến bộ.</footer>
<script>const DATA=__DATA__;
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state={done:[],notes:{}},current=1,voices=[];const KEY='american-english-52-weeks-v1';
try{const a=JSON.parse(localStorage.getItem(KEY)||'null');if(a&&Array.isArray(a.done)&&a.notes&&typeof a.notes==='object')state=a}catch(e){$('#storageStatus').textContent='Trình duyệt chưa cho lưu tiến độ; hãy dùng Xuất tiến độ.'}
function save(){try{localStorage.setItem(KEY,JSON.stringify(state));$('#storageStatus').textContent='Đã lưu trong trình duyệt.'}catch(e){$('#storageStatus').textContent='Không lưu được trên trình duyệt. Hãy xuất tiến độ để giữ bản sao.'}nav()}
function nav(){const q=$('#search').value.toLocaleLowerCase('vi');$('#progress').textContent=`Đã hoàn thành ${state.done.length}/52 tuần`;$('#weeks').innerHTML=DATA.filter(w=>(w.en+' '+w.vi+' '+w.n).toLocaleLowerCase('vi').includes(q)).map(w=>`<button class="nav ${w.n===current?'active':''}" data-week="${w.n}" aria-current="${w.n===current?'page':'false'}">${state.done.includes(w.n)?'✓ ':''}${String(w.n).padStart(2,'0')} · ${esc(w.vi)}</button>`).join('');document.querySelectorAll('[data-week]').forEach(b=>b.onclick=()=>show(Number(b.dataset.week)))}
const listen=(s,label='Nghe')=>`<button data-say="${esc(s)}" aria-label="Nghe: ${esc(s)}">▶ ${label}</button>`;
function show(n){current=n;const w=DATA[n-1];$('#content').innerHTML=`<section><span class="badge">TUẦN ${n}</span><h2>${esc(w.en)}</h2><p class="vi">${esc(w.vi)}</p><p>${esc(w.GOAL)}</p><div class="controls"><button id="prev" ${n===1?'disabled':''}>← Tuần trước</button><button id="next" ${n===52?'disabled':''}>Tuần sau →</button><label><input id="done" type="checkbox" ${state.done.includes(n)?'checked':''}> Đã hoàn thành tuần</label></div></section>
<section><h3>Sáu câu/cụm dùng ngay</h3>${w.P.map(([en,vi],i)=>`<div class="row"><div><strong>${i+1}. ${esc(en)}</strong><p class="vi">${esc(vi)}</p></div>${listen(en)}</div>`).join('')}</section>
<section><h3>Mẫu ngữ pháp</h3><p>${esc(w.GRAMMAR)}</p><h3>Phát âm và nghe</h3><p>${esc(w.SOUND)}</p><h3>Cách dùng và hoàn cảnh</h3><p>${esc(w.REGISTER)}</p></section>
<section><h3>Hội thoại mẫu</h3><p>${listen(w.D.map(d=>d[0]).join(' '),'Nghe cả hội thoại')}</p>${w.D.map(([en,vi],i)=>`<div class="dialogue"><strong>${i%2?'B':'A'}: ${esc(en)}</strong><p class="vi">${esc(vi)}</p>${listen(en)}</div>`).join('')}<h3>Hiểu bài</h3>${w.Q.map(([q,a],i)=>`<p>${i+1}. ${esc(q)}</p><details><summary>Gợi ý trả lời</summary><p>${esc(a)}</p></details>`).join('')}</section>
<section><h3>Luyện nhớ</h3><p>Điền một từ. Với bài nói hoặc dịch, cách diễn đạt khác vẫn có thể đúng.</p>${w.ex.map(([q,a],i)=>`<label for="ex${i}">${i+1}. ${esc(q)}</label><input class="answer" id="ex${i}" autocomplete="off">`).join('')}<button id="check" class="gold">Kiểm tra điền từ</button><p id="result" class="result" role="status"></p><p>4. Sửa lỗi: ${esc(w.FIX[0])}</p><p>5–6. Nói bằng tiếng Anh:</p><ul><li>${esc(w.P[3][1])}</li><li>${esc(w.P[4][1])}</li></ul><details><summary>Xem đáp án 4–6</summary><p>4. ${esc(w.FIX[1])}</p><p>5. ${esc(w.P[3][0])}</p><p>6. ${esc(w.P[4][0])}</p></details></section>
<section><h3>Nhiệm vụ nói</h3><p>${esc(w.TASK)}</p><h3>Đổi tình huống</h3><p>${esc(w.TWIST)}</p><p>Chấm 0–3: hoàn thành nhiệm vụ / dễ hiểu / tương tác / sửa hiểu nhầm / cách diễn đạt. Thu âm trước và sau khi sửa.</p><label for="note">Nhật ký tuần: điều làm được, lỗi cần sửa, ngày ôn lại</label><textarea id="note" placeholder="Ghi ngắn gọn, tránh thông tin nhạy cảm">${esc(state.notes[n]||'')}</textarea><button id="saveNote">Lưu ghi chú</button></section>`;
$('#prev').onclick=()=>show(n-1);$('#next').onclick=()=>show(n+1);$('#done').onchange=e=>{state.done=state.done.filter(x=>x!==n);if(e.target.checked)state.done.push(n);save()};$('#saveNote').onclick=()=>{state.notes[n]=$('#note').value;save()};$('#note').onchange=()=>{state.notes[n]=$('#note').value;save()};$('#check').onclick=()=>{$('#result').textContent=w.ex.map(([q,a],i)=>`${i+1}. ${$('#ex'+i).value.trim().toLowerCase()===a.toLowerCase()?'✓ Đúng':'Chưa đúng — '+a}`).join('\n')};document.querySelectorAll('[data-say]').forEach(b=>b.onclick=()=>speak(b.dataset.say));nav();}
function loadVoices(){if(!('speechSynthesis' in window)){$('#voiceStatus').textContent='Trình duyệt này không hỗ trợ đọc thành tiếng.';return}voices=speechSynthesis.getVoices().filter(v=>v.lang.toLowerCase().replace('_','-')==='en-us');$('#voice').innerHTML=voices.length?voices.map((v,i)=>`<option value="${i}">${esc(v.name)}</option>`).join(''):'<option value="-1">Giọng en-US mặc định</option>';$('#voiceStatus').textContent=voices.length?'Chọn giọng Mỹ có sẵn trên máy.':'Chưa tìm thấy giọng Mỹ riêng; thiết bị sẽ thử giọng en-US mặc định.';}
function speak(t){if(!('speechSynthesis' in window))return;speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang='en-US';u.rate=Number($('#rate').value);if(voices[Number($('#voice').value)])u.voice=voices[Number($('#voice').value)];u.onerror=()=>{$('#voiceStatus').textContent='Chưa phát được âm thanh. Hãy thử giọng khác hoặc kiểm tra giọng tiếng Anh trên máy.'};speechSynthesis.speak(u)}
$('#stop').onclick=()=>window.speechSynthesis?.cancel();$('#toggle').onclick=()=>{const hidden=document.body.classList.toggle('hide-vi');$('#toggle').textContent=hidden?'Hiện nghĩa Việt':'Ẩn nghĩa Việt'};$('#search').oninput=nav;
$('#export').onclick=()=>{state.notes[current]=$('#note').value;save();const url=URL.createObjectURL(new Blob([JSON.stringify({format:'english52-v1',state},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='Tien-do-52-tuan.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
$('#restore').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;const obj=JSON.parse(await f.text());if(obj.format!=='english52-v1'||!Array.isArray(obj.state?.done)||!obj.state?.notes||typeof obj.state.notes!=='object'||Array.isArray(obj.state.notes))throw Error();const valid=obj.state.done.filter(n=>Number.isInteger(n)&&n>=1&&n<=52);state.done=[...new Set([...state.done,...valid])];for(const [k,v] of Object.entries(obj.state.notes)){if(/^([1-9]|[1-4][0-9]|5[0-2])$/.test(k)&&typeof v==='string')state.notes[k]=state.notes[k]?state.notes[k]+'\n--- Bản khôi phục ---\n'+v:v}save();show(current);$('#storageStatus').textContent='Đã bổ sung tiến độ và ghi chú từ bản sao.'}catch(err){$('#storageStatus').textContent='Tệp chưa đúng định dạng tiến độ của tài liệu này.'}e.target.value=''};
if('speechSynthesis' in window){speechSynthesis.onvoiceschanged=loadVoices}loadVoices();show(1);
</script></html>'''
htmlfile.write_text(template.replace('__DATA__',data),encoding='utf-8')

readme='''BỘ TÀI LIỆU TIẾNG ANH MỸ — 52 TUẦN

52 CSV trong thu-muc Tu-Vung: mỗi tuần 6 câu Anh–Việt.
Tat-ca-312-cau.csv: toàn bộ 312 câu. Chỉ nhập tệp tổng HOẶC từng tuần để tránh trùng.
Mã hóa UTF-8 có BOM; cột English,Vietnamese; dấu phân cách phẩy.
Nhập vào chức năng từ vựng của app, xem trước rồi bổ sung. Không dùng như tệp khôi phục toàn bộ app.

52 TXT trong thu-muc Bai-Hoc: nội dung chỉnh sửa được của từng tuần.
Mở bằng trình soạn thảo, sửa theo mục tiêu cá nhân rồi nhập văn bản nếu app hỗ trợ.
Giữ bản sao ngoài app trước khi cập nhật. Gói này không tự đồng bộ với app.

Mở PDF để in; mở HTML bằng Edge/Chrome để nghe và luyện bài.
Tiến độ HTML lưu riêng trong trình duyệt; dùng Xuất tiến độ để giữ bản sao.
Giọng đọc ưu tiên en-US có sẵn trên máy; có giọng cần mạng.
Không bảo đảm nói như người bản xứ sau một năm. Luyện nói thực tế và nhận phản hồi đều đặn.
'''
with zipfile.ZipFile(OUT/'Tu-Vung-52-Tuan.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('HUONG-DAN.txt',readme.encode('utf-8-sig'))
    allrows=[]
    for w in weeks:
        stream=io.StringIO(newline='');writer=csv.writer(stream);writer.writerow(['English','Vietnamese']);writer.writerows(w['P'])
        z.writestr(f"Tu-Vung/Tuan-{w['n']:02d}.csv",stream.getvalue().encode('utf-8-sig'));allrows.extend(w['P'])
        lines=[f"TUẦN {w['n']:02d}: {w['en']} — {w['vi']}",f"MỤC TIÊU: {w['GOAL']}",'','CÂU ANH–VIỆT']
        lines.extend(en+'\n'+vi for en,vi in w['P']);lines+=['','NGỮ PHÁP: '+w['GRAMMAR'],'PHÁT ÂM: '+w['SOUND'],'CÁCH DÙNG: '+w['REGISTER'],'','HỘI THOẠI']
        lines.extend(('A' if i%2==0 else 'B')+': '+en+'\n'+vi for i,(en,vi) in enumerate(w['D']))
        lines+=['','HIỂU BÀI']+[q+'\nĐáp án: '+a for q,a in w['Q']]
        lines+=['','ĐIỀN TỪ']+[q+'\nĐáp án: '+a for q,a in w['ex']]
        lines+=['Sửa lỗi: '+w['FIX'][0],'Đáp án: '+w['FIX'][1],'','NHIỆM VỤ: '+w['TASK'],'ĐỔI TÌNH HUỐNG: '+w['TWIST']]
        z.writestr(f"Bai-Hoc/Tuan-{w['n']:02d}.txt",'\n'.join(lines).encode('utf-8-sig'))
    stream=io.StringIO(newline='');writer=csv.writer(stream);writer.writerow(['English','Vietnamese']);writer.writerows(allrows)
    z.writestr('Tat-ca-312-cau.csv',stream.getvalue().encode('utf-8-sig'))
(ROOT/'work'/'weeks.json').write_text(json.dumps(weeks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'weeks':len(weeks),'phrases':sum(len(w['P']) for w in weeks),'dialogue_turns':sum(len(w['D']) for w in weeks),'pages':page,'outputs':[str(pdf),str(htmlfile),str(OUT/'Tu-Vung-52-Tuan.zip')]},ensure_ascii=False))
