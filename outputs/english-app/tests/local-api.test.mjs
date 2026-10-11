import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import fs from 'node:fs';
import {initialState} from '../app/model.ts';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const testRoot=path.join(root,'work','test-storage-'+Date.now());
const origin='http://127.0.0.1:4191';
async function start(){const child=spawn(process.execPath,[path.join(root,'local-app/server.mjs')],{env:{...process.env,PORT:'4191',GARDEN_DATA_DIR:testRoot},stdio:['ignore','pipe','pipe']});await new Promise((resolve,reject)=>{child.stdout.once('data',resolve);child.once('exit',code=>reject(new Error('Server exited '+code)));child.once('error',reject);});return child;}
async function stop(child){await new Promise(resolve=>{child.once('exit',resolve);child.kill();});}
test('Local app persists updates and files across restart; rejects conflicts and foreign origins',async()=>{
 let child=await start();try{
 let response=await fetch(origin+'/api/health');const health=await response.json();assert.equal(health.app,'english-garden');assert.equal(health.ok,true);assert.equal(health.version,'1.1-52-weeks');assert.match(health.rootId,/^[a-f0-9]{16}$/);response=await fetch(origin+'/');assert.equal(response.status,200);assert.match(await response.text(),/English Garden/);response=await fetch(origin+'/pdf.worker.min.mjs');assert.equal(response.status,200);
 response=await fetch(origin+'/api/state');assert.equal(response.status,200);assert.equal((await response.json()).revision,0);
 const data=initialState();
 response=await fetch(origin+'/api/state',{method:'POST',headers:{'Content-Type':'application/json',Origin:origin},body:JSON.stringify({revision:0,data})});assert.equal(response.status,200);
 data.words[0].vi='Nghĩa đã cập nhật';
 data.progress['us52-week-52']={days:[true,false,true,false,false,false,false],reflection:'Luyện nối âm',script:'My practice script',done:true};
 response=await fetch(origin+'/api/state',{method:'POST',headers:{'Content-Type':'application/json',Origin:origin},body:JSON.stringify({revision:1,data})});assert.equal((await response.json()).revision,2);
 response=await fetch(origin+'/api/state',{method:'POST',headers:{'Content-Type':'application/json',Origin:origin},body:JSON.stringify({revision:1,data})});assert.equal(response.status,409);
 response=await fetch(origin+'/api/state',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://foreign.test'},body:JSON.stringify({revision:2,data})});assert.equal(response.status,403);
 const form=new FormData();form.append('file',new File(['hello | xin chào'],'sample.txt',{type:'text/plain'}));
 response=await fetch(origin+'/api/files',{method:'POST',body:form});assert.equal(response.status,200);const file=await response.json();
 await stop(child);child=await start();
 response=await fetch(origin+'/api/state');const restored=await response.json();assert.equal(restored.revision,2);assert.equal(restored.data.words[0].vi,'Nghĩa đã cập nhật');
 assert.equal(restored.data.lessons.filter(l=>l.course==='us52').length,52);assert.deepEqual(restored.data.progress['us52-week-52'],data.progress['us52-week-52']);
 response=await fetch(origin+'/curriculum/Tieng-Anh-My-52-Tuan.pdf');assert.equal(response.status,200);assert.equal(response.headers.get('content-type'),'application/pdf');assert.ok((await response.arrayBuffer()).byteLength>10000);
 response=await fetch(origin+'/api/files?id='+file.id);assert.equal(await response.text(),'hello | xin chào');
 response=await fetch(origin+'/api/files?id='+file.id,{method:'DELETE'});assert.equal(response.status,200);assert.equal((await fetch(origin+'/api/files?id='+file.id)).status,404);
 assert.ok(fs.existsSync(path.join(testRoot,'english-garden.sqlite')));
 }finally{await stop(child);}
});
