import {test} from 'node:test';
import assert from 'node:assert/strict';
import JSZip from 'jszip';
import * as CFB from 'cfb';
import {extractFile} from '../app/importer.ts';
test('TXT and DOCX extraction preserves English and Vietnamese',async()=>{
 const text='Hello English Garden. Xin chào bạn.';
 assert.equal(await extractFile(new File([text],'sample.txt'),false,()=>{}),text);
 const zip=new JSZip();
 zip.file('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>');
 zip.file('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>');
 zip.file('word/document.xml',`<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>${text}</w:t></w:r></w:p></w:body></w:document>`);
 const bytes=await zip.generateAsync({type:'uint8array'});const result=await extractFile(new File([bytes],'sample.docx'),false,()=>{});assert.equal(result.trim(),text);
});
test('Legacy DOC piece table correctly extracts Unicode text',async()=>{
 const text='I enjoy reading. Tôi thích đọc sách.';const word=new Uint8Array(1024);const v=new DataView(word.buffer);v.setUint16(10,0,true);v.setUint16(32,0,true);v.setUint16(34,0,true);v.setUint16(36,34,true);v.setUint32(38+33*8,0,true);v.setUint32(38+33*8+4,21,true);for(let i=0;i<text.length;i++)v.setUint16(512+i*2,text.charCodeAt(i),true);
 const table=new Uint8Array(21);const t=new DataView(table.buffer);table[0]=2;t.setUint32(1,16,true);t.setUint32(5,0,true);t.setUint32(9,text.length,true);t.setUint32(15,512,true);
 const c=CFB.utils.cfb_new();CFB.utils.cfb_add(c,'WordDocument',word);CFB.utils.cfb_add(c,'0Table',table);const bytes=CFB.write(c,{type:'array'});
 assert.equal(await extractFile(new File([bytes],'sample.doc'),false,()=>{}),text);
});
test('Invalid import formats fail with actionable errors',async()=>{
 await assert.rejects(()=>extractFile(new File(['bad'],'sample.doc'),false,()=>{}),/DOCX/);
 await assert.rejects(()=>extractFile(new File(['bad'],'sample.exe'),false,()=>{}),/Hỗ trợ/);
});
