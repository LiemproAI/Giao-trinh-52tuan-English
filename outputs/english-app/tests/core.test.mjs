import {test} from 'node:test';
import assert from 'node:assert/strict';
import {initialState,parseVocabulary,mergeWords,schedule,newWord,normal,validState} from '../app/model.ts';
test('CSV respects quoted commas, escaped quotes, and multiline fields',()=>{
 const p=parseVocabulary('English,Vietnamese\r\n"Hello, friend","Xin chào, bạn"\r\n"He said ""yes"".","Anh ấy nói có"\r\n"Line one\nline two",Hai dòng');
 assert.equal(p.length,3);assert.equal(p[0].en,'Hello, friend');assert.equal(p[1].en,'He said "yes".');assert.equal(p[2].en,'Line one\nline two');
});
test('Vietnamese pipe and tab imports preserve accents',()=>{assert.deepEqual(parseVocabulary('hello | xin chào\ntravel\tdu lịch'),[{en:'hello',vi:'xin chào'},{en:'travel',vi:'du lịch'}]);});
test('Duplicates are skipped both against existing data and within an import',()=>{const old=newWord('Hello.','xin chào');const r=mergeWords([old],[{en:'HELLO',vi:'chào'},{en:'grow',vi:'lớn lên'},{en:'Grow.',vi:'phát triển'}],'Test');assert.equal(r.added,1);assert.equal(r.duplicates,2);assert.equal(r.words[0].vi,'xin chào');});
test('Recall grades produce increasing review intervals and preserve content',()=>{const w=newWord('grow','lớn lên');const again=schedule(w,0),easy=schedule(w,3);assert.equal(again.interval,0);assert.equal(easy.interval,4);assert.equal(easy.en,w.en);assert.equal(easy.reviews,1);assert.ok(schedule(easy,3).interval>easy.interval);});
test('Backup restores user edits; malformed nested structures are rejected',()=>{const s=initialState();s.words[0].vi='Nghĩa do người dùng sửa';const restored=JSON.parse(JSON.stringify(s));assert.ok(validState(restored));assert.equal(restored.words[0].vi,'Nghĩa do người dùng sửa');assert.equal(validState({...s,words:[{}]}),false);assert.equal(validState({version:2}),false);assert.equal(validState({...s,lessons:[{...s.lessons[0],phrases:[null]}]}),false);assert.equal(validState({...s,words:[s.words[0],s.words[0]]}),false);});
test('Answer comparison ignores case and punctuation but retains distinct words',()=>{assert.equal(normal(' I Enjoy Reading! '),normal('i enjoy reading.'));assert.notEqual(normal('I have a sister'),normal('I have sisters'));});
