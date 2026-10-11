import {test} from 'node:test';
import assert from 'node:assert/strict';
import {initialState,legacyInitialState,addCurriculum,validState} from '../app/model.ts';

test('52 complete weeks cover every learning tab and daily plan',()=>{
 const state=initialState();assert.ok(validState(state));assert.equal(state.lessons.length,52);
 assert.deepEqual(state.lessons.map(l=>l.week),Array.from({length:52},(_,i)=>i+1));
 for(const l of state.lessons){
  assert.equal(l.id,`us52-week-${String(l.week).padStart(2,'0')}`);
  for(const field of ['phrases','patterns','extended','dialogue','qa','exercises','corrections','translations'])assert.ok(l[field].length>0,`${l.week}: ${field}`);
  assert.equal(l.phrases.length,200);assert.equal(new Set(l.phrases.map(p=>p.en)).size,200);assert.equal(l.practiceGroups.length,10);assert.equal(l.dialogue.length,6);assert.equal(l.dailyPlan.length,7);
  for(const field of ['grammar','pronunciation','usage','task','twist'])assert.ok(l[field].length>30);
 }
});
test('upgrade adds course once and preserves old content, reviews, progress and file references',()=>{
 const old=legacyInitialState();old.words[0].reviews=8;old.words[0].vi='Nghĩa cá nhân';
 old.progress[old.lessons[0].id]={done:true,script:'My script',fileId:'old-file',fileName:'my-recording.webm'};
 old.documents.push({id:'personal-doc',title:'My document',text:'Personal notes',created:new Date().toISOString()});
 const upgraded=addCurriculum(old);assert.ok(validState(upgraded));assert.equal(upgraded.lessons.length,58);
 assert.deepEqual(upgraded.words.find(w=>w.id===old.words[0].id),old.words[0]);
 assert.deepEqual(upgraded.progress,old.progress);assert.deepEqual(upgraded.documents,old.documents);
 upgraded.lessons[0].title='Edited course title';upgraded.progress[upgraded.lessons[0].id]={days:[true,false,false,false,false,false,false],reflection:'Practice linking'};
 assert.strictEqual(addCurriculum(upgraded),upgraded);assert.equal(addCurriculum(upgraded).lessons[0].title,'Edited course title');
 assert.ok(validState(JSON.parse(JSON.stringify(upgraded))));
 assert.equal(validState({...upgraded,progress:{bad:{days:[true]}}}),false);
 const removed={...upgraded,lessons:upgraded.lessons.slice(1)};assert.strictEqual(addCurriculum(removed),removed);
});
