export async function extractFile(file:File,ocr:boolean,onProgress:(message:string)=>void):Promise<string> {
 const extension=file.name.split('.').pop()?.toLowerCase();
 if(file.size>20_000_000)throw new Error('Tệp tối đa 20 MB.');
 if(['txt','csv','tsv'].includes(extension||''))return file.text();
 const buffer=await file.arrayBuffer();
 if(extension==='docx'){const module=await import('mammoth/mammoth.browser.js');const mammoth=module.default??module;return (await mammoth.extractRawText({arrayBuffer:buffer})).value;}
 if(extension==='doc')return extractLegacyDoc(new Uint8Array(buffer));
 if(extension==='pdf'){
  const pdfjs=await import('pdfjs-dist');pdfjs.GlobalWorkerOptions.workerSrc='/pdf.worker.min.mjs';
  const pdf=await pdfjs.getDocument({data:buffer}).promise;
  if(pdf.numPages>100)throw new Error('Hãy chia PDF thành các tệp tối đa 100 trang.');
  const texts:string[]=[];let worker:any;
  try {for(let i=1;i<=pdf.numPages;i++){onProgress(`Đọc trang ${i}/${pdf.numPages}…`);const page=await pdf.getPage(i);const content=await page.getTextContent();let text=content.items.map((item:any)=>item.str+(item.hasEOL?'\n':' ')).join('');
   if(ocr&&text.trim().length<30){if(!worker){const t=await import('tesseract.js');worker=await t.createWorker('eng+vie',1,{logger:(m:any)=>{if(m.status==='recognizing text')onProgress(`Nhận dạng trang ${i}: ${Math.round(m.progress*100)}%`);}});}const viewport=page.getViewport({scale:1.5});const canvas=document.createElement('canvas');canvas.width=viewport.width;canvas.height=viewport.height;await page.render({canvas,canvasContext:canvas.getContext('2d')!,viewport}).promise;text=(await worker.recognize(canvas)).data.text;}
   texts.push(text);page.cleanup();}
  }finally{if(worker)await worker.terminate();await pdf.destroy();}
  const result=texts.join('\n\n');if(!result.trim())throw new Error('PDF không có văn bản. Bật OCR để đọc bản scan.');return result;
 }
 throw new Error('Hỗ trợ PDF, DOCX, DOC, TXT, CSV, TSV.');
}
export async function extractLegacyDoc(bytes:Uint8Array):Promise<string> {
 if(bytes[0]!==0xd0||bytes[1]!==0xcf){const text=new TextDecoder().decode(bytes);if(text.startsWith('{\\rtf'))throw new Error('Tệp DOC dạng RTF: hãy lưu lại thành DOCX.');if(/<html/i.test(text))return new DOMParser().parseFromString(text,'text/html').body.textContent||'';throw new Error('Không nhận diện được DOC. Hãy lưu thành DOCX.');}
 const CFB=await import('cfb');const container=CFB.read(bytes,{type:'array'});const word=CFB.find(container,'WordDocument');if(!word?.content)throw new Error('DOC không chứa WordDocument.');
 const data=new Uint8Array(word.content);const view=new DataView(data.buffer,data.byteOffset,data.byteLength);const flags=view.getUint16(10,true);if(flags&0x100)throw new Error('DOC có mật khẩu. Hãy mở khóa rồi nhập lại.');
 const table=CFB.find(container,flags&0x200?'1Table':'0Table');if(!table?.content)throw new Error('DOC cũ chưa hỗ trợ; hãy chuyển sang DOCX.');
 let offset=32;const csw=view.getUint16(offset,true);offset+=2+csw*2;const cslw=view.getUint16(offset,true);offset+=2+cslw*4;const count=view.getUint16(offset,true);offset+=2;if(count<34)throw new Error('DOC quá cũ. Hãy lưu thành DOCX.');
 const fc=view.getUint32(offset+33*8,true),len=view.getUint32(offset+33*8+4,true);const tb=new Uint8Array(table.content);const tv=new DataView(tb.buffer,tb.byteOffset,tb.byteLength);let pos=fc;while(pos<fc+len&&tb[pos]===1){pos+=3+tv.getUint16(pos+1,true);}if(tb[pos]!==2)throw new Error('Không đọc được bảng văn bản DOC. Hãy dùng DOCX.');
 const size=tv.getUint32(pos+1,true);pos+=5;const n=(size-4)/12;let text='';for(let i=0;i<n;i++){const first=tv.getUint32(pos+i*4,true),last=tv.getUint32(pos+(i+1)*4,true);const raw=tv.getUint32(pos+(n+1)*4+i*8+2,true);const compressed=!!(raw&0x40000000);const start=(raw&0x3fffffff)/(compressed?2:1);const end=start+(last-first)*(compressed?1:2);if(end>data.length)throw new Error('DOC bị hỏng.');text+=new TextDecoder(compressed?'windows-1252':'utf-16le').decode(data.slice(start,end));}
 return text.replace(/\r/g,'\n').replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g,'');
}
