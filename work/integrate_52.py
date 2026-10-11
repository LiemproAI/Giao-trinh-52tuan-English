from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
app=root/'outputs/english-app'
weeks=json.loads((root/'work/weeks.json').read_text(encoding='utf-8'))
ext=(root/'work/extensions.txt').read_text(encoding='utf-8').splitlines()
assert len(ext)==52
lessons=[]
for w,expanded in zip(weeks,ext):
    n=w['n']
    plan=[
      'Hiểu sáu câu; cá nhân hóa câu 1–2 bằng thông tin của bạn.',
      'Nghe sáu câu và hội thoại; luyện trọng âm theo ghi chú phát âm.',
      'Nhìn Việt nói Anh; làm điền từ, sửa lỗi và hai câu dịch.',
      'Đổi vai A/B, trả lời hai câu hiểu bài và hỏi thêm ba câu.',
      'Làm nhiệm vụ nói với năm từ khóa; thử tình huống bất ngờ.',
      'Trò chuyện 10–20 phút với bạn học hoặc giáo viên; thu âm và xin góp ý.',
      'Ôn tuần này cùng các tuần cách 1, 3 và 6 tuần; ghi một điều cần cải thiện.'
    ]
    lessons.append(dict(id=f'us52-week-{n:02}',title=w['en'],description=w['vi']+' — '+w['GOAL'],week=n,
      phrases=[dict(en=en,vi=vi) for en,vi in w['P']],
      patterns=[dict(en=en,vi=vi) for en,vi in w['P'][:3]],
      extended=[dict(en=w['P'][0][0],vi=expanded)],
      dialogue=[dict(en=en,vi=vi) for en,vi in w['D']],
      qa=[dict(en=q,vi=a) for q,a in w['Q']],
      exercises=[dict(question=q,answer=a) for q,a in w['ex']],
      corrections=[dict(question=w['FIX'][0],answer=w['FIX'][1])],
      task=w['TASK'],twist=w['TWIST'],grammar=w['GRAMMAR'],pronunciation=w['SOUND'],usage=w['REGISTER'],
      dailyPlan=plan,translations=[dict(en=en,vi=vi) for en,vi in w['P'][3:5]],course='us52',curriculumVersion=1))
(app/'app/curriculum-data.ts').write_text('import type {Lesson} from "./model";\nexport const curriculumLessons:Lesson[] = '+json.dumps(lessons,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
model=app/'app/model.ts';s=model.read_text(encoding='utf-8')
s='import {curriculumLessons} from "./curriculum-data.ts";\n'+s
s=s.replace('week:number;phrases:',"week:number;course?:'us52';curriculumVersion?:number;grammar?:string;pronunciation?:string;usage?:string;twist?:string;dailyPlan?:string[];translations?:Pair[];phrases:")
s=s.replace('score?:number};','score?:number;days?:boolean[];reflection?:string};')
s=s.replace('export function initialState():State {','export function legacyInitialState():State {')
s+='''
// Add stable course IDs once. Existing lessons, edits, reviews and recordings remain intact.
export function addCurriculum(state:State):State {
 const ids=new Set(state.lessons.map(l=>l.id));
 const missing=curriculumLessons.filter(l=>!ids.has(l.id));
 if(!missing.length)return state;
 const added=structuredClone(missing);
 const merged=mergeWords(state.words,added.flatMap(l=>l.phrases),'52 tuần • Tiếng Anh Mỹ');
 return {...state,lessons:[...added,...state.lessons].sort((a,b)=>Number(b.course==='us52')-Number(a.course==='us52')||a.week-b.week),words:merged.words};
}
export function initialState():State {
 return addCurriculum({version:1,words:[],lessons:[],documents:[],progress:{},activity:[]});
}
'''
s=s.replace("&&unique(s.lessons)","&&unique(s.lessons)&&s.lessons.every(l=>['grammar','pronunciation','usage','twist'].every(k=>(l as any)[k]===undefined||text((l as any)[k]))&&(l.dailyPlan===undefined||(Array.isArray(l.dailyPlan)&&l.dailyPlan.every(text)))&&(l.translations===undefined||(Array.isArray(l.translations)&&l.translations.every(pair))))")
s=s.replace("(p.score===undefined||Number.isFinite(p.score)))","(p.score===undefined||Number.isFinite(p.score))&&(p.days===undefined||(Array.isArray(p.days)&&p.days.length===7&&p.days.every(v=>typeof v==='boolean')))&&(p.reflection===undefined||text(p.reflection)))")
model.write_text(s,encoding='utf-8')
p=app/'app/garden.tsx';s=p.read_text(encoding='utf-8')
s=s.replace('day,initialState,makeLesson','day,initialState,addCurriculum,makeLesson')
s=s.replace("const initial=result.data||initialState();revision.current=result.revision;saved.current=result.data?JSON.stringify(initial):'';","const initial=result.data?addCurriculum(result.data):initialState();revision.current=result.revision;saved.current=result.data?JSON.stringify(result.data):'';")
s=s.replace("u.lang='en-GB'","u.lang='en-US'")
s=s.replace("voices.find(v=>v.name===voiceName)||voices.find(v=>v.lang==='en-GB')||voices[0]||null","voices.find(v=>v.name===voiceName)||voices.find(v=>v.lang.toLowerCase()==='en-us')||null")
s=s.replace("window.speechSynthesis.speak(u);","u.onerror=()=>notify('Chưa phát được âm thanh. Hãy chọn giọng khác trong Cài đặt.');window.speechSynthesis.speak(u);")
s=s.replace("v.lang.startsWith('en')","v.lang.toLowerCase().startsWith('en')")
# New course is the default path; the six legacy lessons stay in the personal catalog.
start=s.index(" {page==='lessons'&&!selected&&")
end=s.index("\n {selected&&",start)
s=s[:start]+''' {page==='lessons'&&!selected&&<LessonCatalog data={data} onOpen={openLesson} onEdit={setEditingLesson} onCreate={()=>setEditingLesson(makeLesson('','',[]))}/>}
'''.rstrip()+s[end:]
s=s.replace('<span className="pill">LỘ TRÌNH CỦA BẠN</span>','<span className="pill">52 TUẦN • TIẾNG ANH MỸ</span>')
s=s.replace('Bài học ngắn, thực hành mỗi ngày và kho từ vựng','52 chủ đề, hội thoại và nhiệm vụ luyện nói. Kho từ vựng')
s=s.replace('/ɡrəʊ/','/ɡroʊ/')
s=s.replace('Khu vườn riêng của bạn <span>','V1.1 • Giáo trình 52 tuần <span>')
s=s.replace('<div className="notice">Hãy thay thông tin mẫu bằng thông tin thật của bạn. Sau “enjoy”, dùng động từ thêm -ing.</div>', '''<div className="notice">{l.grammar||'Thay thông tin mẫu bằng thông tin của bạn; chú ý mẫu câu đang học.'}</div>{l.pronunciation&&<section className="panel"><h3>Phát âm & nghe tiếng Anh Mỹ</h3><p>{l.pronunciation}</p></section>}{l.usage&&<section className="panel"><h3>Cách dùng và hoàn cảnh</h3><p>{l.usage}</p></section>}''')
s=s.replace('Thực hành luân phiên vai A và B.','Thực hành luân phiên vai A và B. Sau đó hỏi thêm ba câu chưa có trong mẫu.')
s=s.replace('<Exercises title="2. Sửa lỗi câu" items={l.corrections} onScore={()=>{}}/>','''<Exercises title="2. Sửa lỗi câu" items={l.corrections} onScore={()=>{}}/>{l.translations?.length>0&&<div className="exercises"><h3>3. Nhìn Việt → nói Anh</h3>{l.translations.map((item:Pair,i:number)=><details className="qa" key={i}><summary>{item.vi}</summary><p>{item.en}</p><Button kind="text" onClick={()=>speak(item.en)}><Volume2 size={15}/>Nghe đáp án mẫu</Button></details>)}<p className="muted">Có thể có nhiều cách nói đúng. Thử nói trước khi mở đáp án.</p></div>}''')
s=s.replace('<div className="notice"><b>Nhiệm vụ luyện nói</b><p>{l.task}</p></div>','''<div className="notice"><b>Nhiệm vụ luyện nói</b><p>{l.task}</p>{l.twist&&<><b>Đổi tình huống</b><p>{l.twist}</p></>}</div>{l.dailyPlan&&<section className="panel"><h3>Lịch học bảy ngày</h3><p>45–60 phút mỗi ngày; đánh dấu việc đã làm, không chỉ việc đã đọc.</p>{l.dailyPlan.map((item:string,i:number)=><label className="check-label daily-step" key={i}><input type="checkbox" checked={p.days?.[i]||false} onChange={e=>{const days=Array.from({length:7},(_,j)=>p.days?.[j]||false);days[i]=e.target.checked;progress(l.id,{days});}}/><span><b>Ngày {i+1}</b> · {item}</span></label>)}<label>Tự nhận xét và ngày ôn lại<textarea maxLength={5000} value={p.reflection||''} onChange={e=>progress(l.id,{reflection:e.target.value})} placeholder="Chấm 0–3: hoàn thành nhiệm vụ, dễ hiểu, tương tác, sửa hiểu nhầm, cách diễn đạt. Ghi một điều cần luyện tiếp."/></label></section>}''')
# Show useful local connection guidance instead of a cloud login for local failures.
s=s.replace('<a className="btn primary" href="/signin-with-chatgpt?return_to=/" target="_top">Đăng nhập với ChatGPT</a>','{localMode?<p>Mở MO-APP.cmd trước, rồi dùng địa chỉ trong data/app-url.txt.</p>:<a className="btn primary" href="/signin-with-chatgpt?return_to=/" target="_top">Đăng nhập với ChatGPT</a>}')
catalog='''
function LessonCatalog({data,onOpen,onEdit,onCreate}:any){
 const [query,setQuery]=useState(''),[scope,setScope]=useState('course');
 const list:Lesson[]=data.lessons.filter((l:Lesson)=>scope==='course'?l.course==='us52':l.course!=='us52');
 const done=list.filter(l=>data.progress[l.id]?.done).length;
 const shown=list.filter(l=>normal(l.title+' '+l.description+' '+l.week).includes(normal(query)));
 return <><Heading eyebrow="52 WEEKS · AMERICAN ENGLISH" title="Học tiếng Anh trong 52 tuần" subtitle="Đời sống, du lịch, công việc và giao tiếp xã hội. Luyện đều, ôn cách quãng và tăng trò chuyện thực tế." action={<Button kind="primary" onClick={onCreate}><Plus size={17}/>Tạo bài học</Button>}/><div className="progress-banner"><div><b>{done} / {list.length} bài đã hoàn thành</b><p>{scope==='course'?'Bốn chặng: tuần 13, 26, 39 và 52.':'Bài đã nhập, bài tự soạn và bài mẫu cũ.'}</p></div><div className="progress-track"><span style={{width:`${list.length?done/list.length*100:0}%`}}/></div></div><div className="toolbar"><label>Chọn bộ học<select value={scope} onChange={e=>setScope(e.target.value)}><option value="course">Giáo trình 52 tuần</option><option value="personal">Bài cá nhân & bài mẫu cũ</option></select></label><div className="search"><Search size={18}/><input aria-label="Tìm chủ đề hoặc tuần" placeholder="Tìm chủ đề hoặc tuần…" value={query} onChange={e=>setQuery(e.target.value)}/></div><label>Đến tuần<select value="" onChange={e=>{if(e.target.value)onOpen(e.target.value);}}><option value="">Chọn tuần để học</option>{list.map(l=><option key={l.id} value={l.id}>Tuần {l.week} · {l.title}</option>)}</select></label></div><section className="notice">Mục tiêu là nói rõ, tự nhiên và tự tin. Không bảo đảm đạt trình độ người bản xứ sau một năm. Mỗi tuần có lịch bảy ngày trong phần Nộp bài.</section><div className="lesson-list">{shown.map(l=><div className="lesson-row" key={l.id}><button className="row-open" onClick={()=>onOpen(l.id)}><span className="lesson-number">{String(l.week).padStart(2,'0')}</span><div><small>Tuần {l.week} · {l.phrases.length} câu · {data.progress[l.id]?.done?'Đã hoàn thành':'Sẵn sàng học'}</small><h3>{l.title}</h3><p>{l.description}</p></div><ArrowRight size={19}/></button><button className="icon-btn" aria-label={`Sửa ${l.title}`} onClick={()=>onEdit(l)}><Pencil size={16}/></button></div>)}</div>{!shown.length&&<Empty title="Không tìm thấy bài" text="Thử chủ đề khác hoặc đổi bộ học."/>}</>;
}
'''
s+=catalog
p.write_text(s,encoding='utf-8')
with (app/'app/design.css').open('a',encoding='utf-8') as f:f.write('\n.daily-step{align-items:flex-start!important;line-height:1.65;margin:12px 0}.daily-step input{flex-shrink:0;margin-top:5px}.toolbar label{min-width:180px}.toolbar .search{flex:1}.lesson-content .panel p{line-height:1.75}\n')
print('Integrated 52 lessons, migrations, US voice, catalog and daily progress.')
