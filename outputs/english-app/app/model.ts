import {curriculumLessons} from "./curriculum-data.ts";
import {legacyCourse} from "./curriculum-legacy.ts";
export type Word = {id:string;en:string;vi:string;example:string;tag:string;due:string;interval:number;reviews:number};
export type Pair = {en:string;vi:string};
export type Lesson = {id:string;title:string;description:string;week:number;course?:'us52';curriculumVersion?:number;grammar?:string;pronunciation?:string;usage?:string;twist?:string;dailyPlan?:string[];translations?:Pair[];practiceGroups?:string[];phrases:Pair[];patterns:Pair[];extended:Pair[];dialogue:Pair[];qa:Pair[];exercises:{question:string;answer:string}[];corrections:{question:string;answer:string}[];task:string};
export type Doc = {id:string;title:string;text:string;fileId?:string;created:string};
export type Progress = {done?:boolean;script?:string;fileId?:string;fileName?:string;score?:number;days?:boolean[];reflection?:string};
export type State = {version:1;curriculumVersion?:number;words:Word[];lessons:Lesson[];documents:Doc[];progress:Record<string,Progress>;activity:string[]};
export const uid=()=>crypto.randomUUID();
export const day=()=>new Date().toISOString().slice(0,10);
export const normal=(s:string)=>s.toLocaleLowerCase().normalize('NFKC').replace(/[.,!?;:]/g,'').replace(/\s+/g,' ').trim();
export function newWord(en:string,vi='',example='',tag='Cá nhân'):Word {return {id:uid(),en:en.trim(),vi:vi.trim(),example,tag,due:day(),interval:0,reviews:0};}
export function schedule(word:Word, grade:number):Word {const interval=grade===0?0:grade===1?1:Math.max(grade===3?4:2, Math.round((word.interval||1)*(grade===3?2.5:1.8)));const d=new Date();d.setUTCDate(d.getUTCDate()+interval);return {...word,interval,due:d.toISOString().slice(0,10),reviews:word.reviews+1};}
export function splitCSV(text:string):string[][] {const rows:string[][]=[];let row:string[]=[],field='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(field);field='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field);if(row.some(v=>v.trim()))rows.push(row);row=[];field='';}else field+=c;}row.push(field);if(row.some(v=>v.trim()))rows.push(row);return rows;}
export function parseVocabulary(text:string):Pair[] {const clean=text.replace(/^\uFEFF/,'').trim();const rows=clean.includes(',')&&!clean.includes('\t')&&!clean.includes('|')?splitCSV(clean):clean.split(/\r?\n/).map(line=>line.split(/\t|\s*\|\s*|\s+[—–]\s+|\s+-\s+/));return rows.filter(r=>r[0]?.trim()).filter((r,i)=>!(i===0&&/^(english|en|word|từ|từ vựng)$/i.test(r[0].trim()))).map(r=>({en:r[0].trim(),vi:(r[1]||'').trim()}));}
export function mergeWords(existing:Word[],incoming:Pair[],tag:string) {const keys=new Set(existing.map(w=>normal(w.en)));let duplicates=0;const added:Word[]=[];for(const pair of incoming){const key=normal(pair.en);if(keys.has(key)){duplicates++;continue;}keys.add(key);if(pair.en.trim())added.push(newWord(pair.en,pair.vi,'',tag));}return {words:[...existing,...added],added:added.length,duplicates};}
const pair=(en:string,vi:string)=>({en,vi});
export function makeLesson(title:string,description:string,phrases:Pair[],week=1):Lesson {return {id:uid(),title,description,week,phrases,patterns:phrases.slice(0,3),extended:[],dialogue:[],qa:[],exercises:phrases.slice(0,6).map(p=>{const parts=p.en.split(' ');return {question:['____',...parts.slice(1)].join(' '),answer:parts[0]};}),corrections:[],task:'Nói 5–7 câu theo nội dung bài. Ghi âm và nghe lại; cố gắng nói tự nhiên, không đọc.'};}
export function legacyInitialState():State {
 const topics:[string,string,Pair[]][]=[
 ['Introduce Yourself','Giới thiệu bản thân, gia đình và sở thích.',[pair('My name is Linh.','Tên tôi là Linh.'),pair('I have one sister.','Tôi có một chị gái.'),pair('I live with my family.','Tôi sống cùng gia đình.'),pair('I enjoy reading books.','Tôi thích đọc sách.'),pair('I work as a teacher.','Tôi làm giáo viên.'),pair('I am single.','Tôi độc thân.')]],
 ['My English Goal','Nói về mục tiêu và lý do học tiếng Anh.',[pair('I want to speak English confidently.','Tôi muốn nói tiếng Anh tự tin.'),pair('I study English every day.','Tôi học tiếng Anh mỗi ngày.'),pair('My goal is to travel abroad.','Mục tiêu của tôi là đi du lịch nước ngoài.'),pair('I practice for twenty minutes.','Tôi luyện tập trong hai mươi phút.'),pair('I learn from my mistakes.','Tôi học từ những lỗi của mình.')]],
 ['My Daily Routine','Kể về một ngày của bạn.',[pair('I wake up at seven.','Tôi thức dậy lúc bảy giờ.'),pair('I have breakfast at home.','Tôi ăn sáng ở nhà.'),pair('I go to work by bus.','Tôi đi làm bằng xe buýt.'),pair('I cook dinner in the evening.','Tôi nấu bữa tối vào buổi tối.'),pair('I go to bed at ten.','Tôi đi ngủ lúc mười giờ.')]],
 ['Work & Study','Mô tả công việc và việc học.',[pair('I work in a small team.','Tôi làm việc trong một nhóm nhỏ.'),pair('I attend meetings every Monday.','Tôi dự họp vào mỗi thứ Hai.'),pair('I am learning a new skill.','Tôi đang học một kỹ năng mới.'),pair('I help my colleagues.','Tôi giúp đồng nghiệp.'),pair('I enjoy solving problems.','Tôi thích giải quyết vấn đề.')]],
 ['At a Café','Gọi đồ uống và hỏi giá.',[pair('Could I have a coffee, please?','Cho tôi một ly cà phê được không?'),pair('I would like a cup of tea.','Tôi muốn một tách trà.'),pair('How much is it?','Giá bao nhiêu?'),pair('Can I pay by card?','Tôi có thể trả bằng thẻ không?'),pair('That is all, thank you.','Vậy là đủ, cảm ơn.')]],
 ['Travel & Directions','Hỏi đường và giao tiếp khi đi du lịch.',[pair('Where is the train station?','Ga tàu ở đâu?'),pair('How can I get there?','Tôi có thể đến đó bằng cách nào?'),pair('Turn left at the next street.','Rẽ trái ở đường tiếp theo.'),pair('I would like to book a room.','Tôi muốn đặt một phòng.'),pair('I have a reservation.','Tôi đã đặt chỗ.')]]];
 const lessons=topics.map(([t,d,p],i)=>makeLesson(t,d,p,i<4?1:2));
 lessons[0].patterns=[pair('I am…','Tên / trạng thái / nghề nghiệp'),pair('I have…','Người thân / thú cưng'),pair('I enjoy + V-ing','Hoạt động bạn thích')];
 lessons[0].extended=[pair('I have one sister.','I have one sister, and she is younger than me.'),pair('I live with my family.','I live with my family in a small apartment.'),pair('I enjoy reading books.','I enjoy reading books because they help me relax.')];
 lessons[0].dialogue=[pair('Do you have any siblings?','Bạn có anh chị em không?'),pair('Yes, I have one sister.','Có, tôi có một chị gái.'),pair('What do you enjoy doing?','Bạn thích làm gì?'),pair('I enjoy reading books.','Tôi thích đọc sách.')];
 lessons[0].qa=[pair('Do you have any siblings?','Yes, I have one sister.'),pair('Who do you live with?','I live with my family.'),pair('What do you enjoy doing?','I enjoy reading books.'),pair('What do you do?','I work as a teacher.')];
 lessons[0].corrections=[{question:'I have one sisters.',answer:'I have one sister.'},{question:'I enjoy read books.',answer:'I enjoy reading books.'},{question:'I am live with my family.',answer:'I live with my family.'}];
 return {version:1,words:lessons.flatMap(l=>l.phrases.map(p=>newWord(p.en,p.vi,'',l.title))),lessons,documents:[],progress:{},activity:[]};
}
export function validState(value:unknown):value is State {
 const s=value as State;const text=(v:unknown)=>typeof v==='string';const pair=(v:any)=>!!v&&text(v.en)&&text(v.vi);const exercise=(v:any)=>!!v&&text(v.question)&&text(v.answer);const unique=(list:{id:string}[])=>new Set(list.map(v=>v.id)).size===list.length;
 return !!s&&s.version===1&&Array.isArray(s.words)&&s.words.every(w=>!!w&&text(w.id)&&text(w.en)&&text(w.vi)&&text(w.tag)&&text(w.example)&&text(w.due)&&/^\d{4}-\d{2}-\d{2}$/.test(w.due)&&Number.isFinite(w.interval)&&w.interval>=0&&Number.isFinite(w.reviews)&&w.reviews>=0)&&unique(s.words)
 &&Array.isArray(s.lessons)&&s.lessons.every(l=>!!l&&text(l.id)&&text(l.title)&&text(l.description)&&text(l.task)&&Number.isInteger(l.week)&&l.week>=1&&['phrases','patterns','extended','dialogue','qa'].every(k=>Array.isArray((l as any)[k])&&(l as any)[k].every(pair))&&['exercises','corrections'].every(k=>Array.isArray((l as any)[k])&&(l as any)[k].every(exercise)))&&unique(s.lessons)&&s.lessons.every(l=>['grammar','pronunciation','usage','twist'].every(k=>(l as any)[k]===undefined||text((l as any)[k]))&&(l.dailyPlan===undefined||(Array.isArray(l.dailyPlan)&&l.dailyPlan.every(text)))&&(l.translations===undefined||(Array.isArray(l.translations)&&l.translations.every(pair))))
 &&s.lessons.every(l=>l.practiceGroups===undefined||(Array.isArray(l.practiceGroups)&&l.practiceGroups.every(text)))
 &&Array.isArray(s.documents)&&s.documents.every(d=>!!d&&text(d.id)&&text(d.text)&&text(d.title)&&text(d.created)&&(d.fileId===undefined||text(d.fileId)))&&unique(s.documents)
 &&!!s.progress&&typeof s.progress==='object'&&!Array.isArray(s.progress)&&Object.values(s.progress).every(p=>!!p&&typeof p==='object'&&(p.done===undefined||typeof p.done==='boolean')&&(p.script===undefined||text(p.script))&&(p.fileId===undefined||text(p.fileId))&&(p.fileName===undefined||text(p.fileName))&&(p.score===undefined||Number.isFinite(p.score))&&(p.days===undefined||(Array.isArray(p.days)&&p.days.length===7&&p.days.every(v=>typeof v==='boolean')))&&(p.reflection===undefined||text(p.reflection)))
 &&Array.isArray(s.activity)&&s.activity.every(v=>text(v)&&/^\d{4}-\d{2}-\d{2}$/.test(v));
}

// Upgrade course fields only when they still match the old edition; keep personal edits.
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
