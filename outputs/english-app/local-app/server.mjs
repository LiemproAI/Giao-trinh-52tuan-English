import http from 'node:http';
import {DatabaseSync} from 'node:sqlite';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const rootId=crypto.createHash('sha256').update(path.resolve(root).toLowerCase()).digest('hex').slice(0,16);
const dataRoot=process.env.GARDEN_DATA_DIR||path.join(root,'data');fs.mkdirSync(path.join(dataRoot,'files'),{recursive:true});
const db=new DatabaseSync(path.join(dataRoot,'english-garden.sqlite'));
db.exec('PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, data TEXT NOT NULL, revision INTEGER NOT NULL, updated_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, name TEXT NOT NULL);');
const port=Number(process.env.PORT||4173);
const valid=(s)=>s&&s.version===1&&Array.isArray(s.words)&&s.words.every(w=>typeof w.id==='string'&&typeof w.en==='string'&&typeof w.vi==='string'&&typeof w.due==='string'&&Number.isFinite(w.interval)&&Number.isFinite(w.reviews))&&Array.isArray(s.lessons)&&s.lessons.every(l=>typeof l.id==='string'&&typeof l.title==='string'&&['phrases','patterns','extended','dialogue','qa','exercises','corrections'].every(k=>Array.isArray(l[k])))&&Array.isArray(s.documents)&&s.documents.every(d=>typeof d.id==='string'&&typeof d.text==='string'&&typeof d.title==='string')&&s.progress&&typeof s.progress==='object'&&Array.isArray(s.activity);
const json=(res,status,body)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});res.end(JSON.stringify(body));};
async function body(req,max){const chunks=[];let length=0;for await(const c of req){length+=c.length;if(length>max)throw Object.assign(new Error('Dữ liệu vượt giới hạn.'),{status:413});chunks.push(c);}return Buffer.concat(chunks);}
const types={'.pdf':'application/pdf','.zip':'application/zip','.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.webmanifest':'application/manifest+json','.png':'image/png','.woff2':'font/woff2'};
const speechJobs=new Map();
const server=http.createServer(async(req,res)=>{try{
 const origin=`http://127.0.0.1:${port}`;const hostname=req.headers.host;
 if(hostname!==`127.0.0.1:${port}`&&hostname!==`localhost:${port}`){json(res,403,{error:'Host không hợp lệ.'});return;}
 const url=new URL(req.url,origin);
 if(url.pathname==='/api/health'&&req.method==='GET'){json(res,200,{app:'english-garden',ok:true,version:'1.1-52-weeks',rootId});return;}
 if(req.headers.origin&&!['http://127.0.0.1:'+port,'http://localhost:'+port].includes(req.headers.origin)){json(res,403,{error:'Nguồn yêu cầu không hợp lệ.'});return;}

 if(url.pathname==='/api/tts'&&req.method==='POST'){
  const value=JSON.parse((await body(req,30_000)).toString());
  if(typeof value.text!=='string'||!value.text.trim()||value.text.length>5000){json(res,400,{error:'Nội dung đọc phải từ 1 đến 5.000 ký tự.'});return;}
  const text=value.text.trim();
  const cacheRoot=path.join(dataRoot,'speech-haidang');fs.mkdirSync(cacheRoot,{recursive:true});
  const key=crypto.createHash('sha256').update('haidang-v1:'+text).digest('hex');
  const filename=path.join(cacheRoot,key+'.wav');
  try {
   if(!fs.existsSync(filename)){
    if(!speechJobs.has(key))speechJobs.set(key,(async()=>{
     const health=await fetch('http://127.0.0.1:8001/api/health',{signal:AbortSignal.timeout(10000)});
     if(!health.ok||(await health.json()).status?.loaded!==true)throw new Error('Model VieNeu chưa sẵn sàng. Hãy chờ model tải xong.');
     const response=await fetch('http://127.0.0.1:8001/api/voices',{signal:AbortSignal.timeout(10000)});
     if(!response.ok)throw new Error('Không lấy được danh sách giọng VieNeu.');
     const voice=(await response.json()).voices?.find(v=>v.id==='Hải Đăng');
     if(!voice)throw new Error('VieNeu chưa có giọng Hải Đăng.');
     const audio=await fetch('http://127.0.0.1:8001/api/tts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,voice:voice.id,temperature:0.8,top_k:25}),signal:AbortSignal.timeout(240000)});
     if(audio.status!==200){const detail=await audio.json();throw new Error(detail.detail||'VieNeu không tạo được âm thanh.');}
     const bytes=Buffer.from(await audio.arrayBuffer());
     if(bytes.toString('ascii',0,4)!=='RIFF'||bytes.toString('ascii',8,12)!=='WAVE')throw new Error('VieNeu trả về tệp không phải WAV.');
     fs.writeFileSync(filename,bytes);
    })().finally(()=>speechJobs.delete(key)));
    await speechJobs.get(key);
   }
   res.writeHead(200,{'Content-Type':'audio/wav','Cache-Control':'no-store'});fs.createReadStream(filename).pipe(res);return;
  }catch(error){json(res,503,{error:'Giọng Hải Đăng: '+(error.message||'Hãy mở VieNeu Studio tại cổng 8001.')});return;}
 }

 if(url.pathname==='/api/state'){
  if(req.method==='GET'){const row=db.prepare('SELECT * FROM state WHERE id=1').get();json(res,200,{data:row?JSON.parse(row.data):null,revision:row?.revision||0,updatedAt:row?.updated_at||null});return;}
  if(req.method==='POST'){const value=JSON.parse((await body(req,20_000_000)).toString());if(!valid(value.data)||!Number.isInteger(value.revision)||value.revision<0){json(res,400,{error:'Dữ liệu không hợp lệ.'});return;}const now=new Date().toISOString();const result=value.revision===0?db.prepare('INSERT OR IGNORE INTO state(id,data,revision,updated_at) VALUES(1,?,1,?)').run(JSON.stringify(value.data),now):db.prepare('UPDATE state SET data=?,revision=revision+1,updated_at=? WHERE id=1 AND revision=?').run(JSON.stringify(value.data),now,value.revision);if(!result.changes){json(res,409,{error:'Dữ liệu đã thay đổi ở cửa sổ khác. Sao lưu bản hiện tại, sau đó tải lại.'});return;}json(res,200,{revision:value.revision+1,updatedAt:now});return;}
 }
 if(url.pathname==='/api/files'){
  if(req.method==='POST'){const bytes=await body(req,21_000_000);const request=new Request(origin+req.url,{method:'POST',headers:{'Content-Type':req.headers['content-type']||''},body:bytes});const form=await request.formData();const f=form.get('file');if(!(f instanceof File)||f.size>20_000_000||! /\.(pdf|docx?|txt|csv|tsv|json|webm|wav|mp4|m4a|ogg)$/i.test(f.name)){json(res,400,{error:'Tệp không hợp lệ hoặc vượt 20 MB.'});return;}const id=crypto.randomUUID();fs.writeFileSync(path.join(dataRoot,'files',id),Buffer.from(await f.arrayBuffer()));db.prepare('INSERT INTO files (id,name) VALUES (?,?)').run(id,f.name);json(res,200,{id,name:f.name,size:f.size});return;}
  const id=url.searchParams.get('id')||'';if(!/^[a-f0-9-]{36}$/.test(id)){json(res,400,{error:'Mã tệp không hợp lệ.'});return;}const f=db.prepare('SELECT name FROM files WHERE id=?').get(id);
  if(req.method==='DELETE'){if(f){fs.rmSync(path.join(dataRoot,'files',id),{force:true});db.prepare('DELETE FROM files WHERE id=?').run(id);}json(res,200,{ok:true});return;}
  if(req.method==='GET'&&f){res.writeHead(200,{'Content-Type':'application/octet-stream','Content-Disposition':`attachment; filename*=UTF-8''${encodeURIComponent(f.name)}`,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});fs.createReadStream(path.join(dataRoot,'files',id)).pipe(res);return;}json(res,404,{error:'Không tìm thấy tệp.'});return;
 }
 if(['/signin-with-chatgpt','/signout-with-chatgpt'].includes(url.pathname)){res.writeHead(302,{Location:'/'});res.end();return;}
 if(!['GET','HEAD'].includes(req.method)){json(res,405,{error:'Method not allowed'});return;}
 const requested=decodeURIComponent(url.pathname);let filename=path.resolve(root,'public','.'+requested);const publicRoot=path.resolve(root,'public');if(filename!==publicRoot&&!filename.startsWith(publicRoot+path.sep)){json(res,403,{error:'Forbidden'});return;}
 if(requested==='/')filename=path.join(publicRoot,'index.html');if(!fs.existsSync(filename)||!fs.statSync(filename).isFile()){json(res,404,{error:'Not found'});return;}
 res.writeHead(200,{'Content-Type':types[path.extname(filename)]||'application/octet-stream','X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'});if(req.method==='HEAD')res.end();else fs.createReadStream(filename).pipe(res);
 }catch(error){json(res,error.status||400,{error:error.message||'Lỗi xử lý dữ liệu.'});}});
server.listen(port,'127.0.0.1',()=>console.log(`English Garden: http://127.0.0.1:${port}\nDữ liệu: ${dataRoot}\nChỉ truy cập trên máy này. Giữ tiến trình mở khi dùng app.`));
const stop=()=>server.close(()=>{db.close();process.exit(0);});process.on('SIGINT',stop);process.on('SIGTERM',stop);
server.on('error',error=>{console.error(error.code==='EADDRINUSE'?`Cong ${port} dang duoc su dung. Hay mo app bang MO-APP.cmd de tu chon cong khac.`:error.message);db.close();process.exit(1);});
