import {test} from 'node:test';
import assert from 'node:assert/strict';
import {legacyCourse} from '../app/curriculum-legacy.ts';
import {addCurriculum,validState,newWord,parseVocabulary} from '../app/model.ts';
import fs from 'node:fs';

test('200-sentence upgrade preserves edits, deletions, recordings and scheduling',()=>{
 const lessons=structuredClone(Object.values(legacyCourse));
 const original=lessons[0].phrases[0].en;
 lessons[0].title='My custom title';lessons[0].task='My custom task';lessons[0].phrases[0].vi='My own meaning';
 lessons[1].phrases.shift();lessons.splice(2,1);
 const word={...newWord(original,'Custom meaning'),reviews:17,interval:32};
 const old={version:1,curriculumVersion:1,lessons,words:[word],documents:[{id:'doc',title:'Notes',text:'Keep me',created:'2026-10-11'}],progress:{'us52-week-01':{done:true,script:'My script',fileId:'recording',days:[true,false,false,false,false,false,false]}},activity:['2026-10-11']};
 const result=addCurriculum(old);assert.ok(validState(result));assert.equal(result.curriculumVersion,2);
 assert.equal(result.lessons.length,51);assert.ok(!result.lessons.some(l=>l.week===3));
 assert.equal(result.lessons[0].title,'My custom title');assert.equal(result.lessons[0].task,'My custom task');
 assert.equal(result.lessons[0].phrases[0].vi,'My own meaning');
 assert.equal(result.lessons[0].phrases.length,200);
 assert.equal(result.lessons.find(l=>l.week===2).phrases.length,199);
 assert.deepEqual(result.words.find(w=>w.id===word.id),word);
 assert.deepEqual(result.progress,old.progress);assert.deepEqual(result.documents,old.documents);
 assert.strictEqual(addCurriculum(result),result);
});

test('each downloadable weekly CSV imports 200 bilingual entries',()=>{
 for(let week=1;week<=52;week++){
  const path=`../Giao-Trinh-52-Tuan-200-Cau/Tuan-${String(week).padStart(2,'0')}-200-Cau.csv`;
  const pairs=parseVocabulary(fs.readFileSync(path,'utf8'));assert.equal(pairs.length,200);
  assert.ok(pairs.every(p=>p.en&&p.vi));
 }
});
