from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
app=root/'outputs/english-app'
old=json.loads((root/'work/curriculum-v1.json').read_text(encoding='utf-8'))
(app/'app/curriculum-legacy.ts').write_text('export const legacyCourse = '+json.dumps({l['id']:l for l in old},ensure_ascii=False)+';\n',encoding='utf-8')
p=app/'app/model.ts';s=p.read_text(encoding='utf-8')
s=s.replace('export type Word', 'import {legacyCourse} from "./curriculum-legacy";\nexport type Word',1)
s=s.replace('translations?:Pair[];phrases:', 'translations?:Pair[];practiceGroups?:string[];phrases:')
start=s.index('// Add stable course IDs')
s=s[:start]+'''// Upgrade course fields only when they still match the old edition; keep personal edits.
export function addCurriculum(state:State):State {
 if((state.curriculumVersion||0)>=2)return state;
 const known=new Set(state.lessons.map(l=>l.id));
 const lessons=state.lessons.map(lesson=>{
  const target=curriculumLessons.find(l=>l.id===lesson.id);
  if(!target)return lesson;
  const previous=legacyCourse[lesson.id as keyof typeof legacyCourse];
  if(!previous)return lesson;
  const result={...lesson};
  for(const key of ['description','dailyPlan','task','twist','usage','qa','exercises','translations'] as const){
   if(JSON.stringify(lesson[key])===JSON.stringify(previous[key]))Object.assign(result,{[key]:structuredClone(target[key])});
  }
  const isUnedited=JSON.stringify(lesson.phrases)===JSON.stringify(previous.phrases);
  if(isUnedited)result.phrases=structuredClone(target.phrases);
  else {
   // Avoid restoring deleted old phrases; append only the new practice material.
   const keys=new Set(lesson.phrases.map(p=>normal(p.en)));
   const oldKeys=new Set(previous.phrases.map(p=>normal(p.en)));
   result.phrases=[...lesson.phrases,...target.phrases.filter(p=>!oldKeys.has(normal(p.en))&&!keys.has(normal(p.en)))];
  }
  if(isUnedited)result.practiceGroups=structuredClone(target.practiceGroups);
  result.curriculumVersion=2;
  return result;
 });
 // A version-one marker means intentional deletions must stay deleted.
 const missing=state.curriculumVersion===1?[]:curriculumLessons.filter(l=>!known.has(l.id));
 lessons.push(...structuredClone(missing));
 const merged=mergeWords(state.words,lessons.filter(l=>l.course==='us52').flatMap(l=>l.phrases),'52 tuần • 200 câu/tuần');
 return {...state,curriculumVersion:2,lessons:lessons.sort((a,b)=>Number(b.course==='us52')-Number(a.course==='us52')||a.week-b.week),words:merged.words};
}
export function initialState():State {
 return addCurriculum({version:1,words:[],lessons:[],documents:[],progress:{},activity:[]});
}
'''
p.write_text(s,encoding='utf-8')
for p in [root/'outputs/server.mjs',app/'local-app/server.mjs']:
 s=p.read_text(encoding='utf-8').replace('body(req,4_000_000)','body(req,20_000_000)')
 p.write_text(s,encoding='utf-8')
p=app/'app/garden.tsx';s=p.read_text(encoding='utf-8')
s=s.replace('f.size>4_000_000','f.size>20_000_000').replace('Bản sao lưu tối đa 4 MB.','Bản sao lưu tối đa 20 MB.')
s=s.replace("const [tab,setTab]=useState(0),[revealed", "const [tab,setTab]=useState(0),[group,setGroup]=useState(0),[revealed")
s=s.replace('const phrases:Pair[]=l.phrases;', 'const allPhrases:Pair[]=l.phrases;const offset=group*20;const phrases:Pair[]=allPhrases.length>40?allPhrases.slice(offset,offset+20):allPhrases;')
s=s.replace('● {phrases.length} câu thực hành', '● {allPhrases.length} câu thực hành')
insert='''{allPhrases.length>40&&<section className="panel"><div className="toolbar"><label>Chọn nhóm luyện 20 câu<select aria-label="Chọn nhóm luyện 20 câu" value={group} onChange={e=>{setGroup(Number(e.target.value));setDrill(0);setRunning(false);setSeconds(3);setShowAnswer(false);setRevealed(new Set());}}>{Array.from({length:Math.ceil(allPhrases.length/20)},(_,i)=><option key={i} value={i}>Nhóm {i+1} · Câu {i*20+1}–{Math.min((i+1)*20,allPhrases.length)}{l.practiceGroups?.[i]?' · '+l.practiceGroups[i]:''}</option>)}</select></label></div><p>Câu {offset+1}–{Math.min(offset+20,allPhrases.length)} / {allPhrases.length}. Nhóm này áp dụng cho Phrases, Flashcards, phản xạ 3 giây và Rapid Fire.</p><p className="muted">Các câu mở rộng luyện chuyển mẫu giao tiếp sang tình huống thực tế. Học cách đáp lại và hỏi thêm, không chỉ thuộc lòng câu mẫu.</p></section>}'''
s=s.replace('<div className="lesson-tabs" role="tablist">',insert+'<div className="lesson-tabs" role="tablist">')
s=s.replace("String(i+1).padStart(2,'0')", "String(offset+i+1).padStart(3,'0')")
# That replacement also touches unrelated lists: restrict those back to their own numbering.
first=s.index('function LessonView')
s=s[:first].replace("String(offset+i+1).padStart(3,'0')", "String(i+1).padStart(2,'0')")+s[first:]
s=s.replace('aria-label={`Nghe câu ${i+1}`}', 'aria-label={`Nghe câu ${offset+i+1}`}')
s=s.replace('45–60 phút mỗi ngày;', '60–90 phút mỗi ngày;')
s=s.replace('Không bảo đảm đạt trình độ người bản xứ sau một năm. Mỗi tuần có lịch bảy ngày trong phần Nộp bài.', '200 câu/tuần, 10 nhóm tình huống, tăng dần từ nền tảng đến mục tiêu B2. Lịch bảy ngày và kiểm tra chặng nằm trong Nộp bài. Đạt B2 cần đánh giá nghe, nói, đọc, viết trên tài liệu và tình huống mới; app không tự chứng nhận trình độ. Dấu hoàn thành cũ không có nghĩa đã luyện hết câu bổ sung.')
s=s.replace('<a className="btn" href="/curriculum/Tieng-Anh-My-52-Tuan.pdf" download>Sách PDF 125 trang</a><a className="btn" href="/curriculum/Tu-Vung-52-Tuan.zip" download>Từ vựng & bài học để chỉnh sửa</a>', '<a className="btn" href="/curriculum/Tieng-Anh-52-Tuan-10400-Cau.html" target="_blank" rel="noreferrer">Sách đầy đủ 10.400 câu</a><a className="btn" href="/curriculum/Giao-Trinh-52-Tuan-200-Cau.zip" download>52 bộ CSV/TXT & hướng dẫn B2</a>')
p.write_text(s,encoding='utf-8')
print('Integrated safe migration, groups of 20, new downloads and 20 MB local storage limit.')
