import JSZip from 'jszip';
import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd();
async function packageFolder(folder,filename,exclude){const zip=new JSZip();function add(dir,prefix=''){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){if(exclude.has(entry.name))continue;const full=path.join(dir,entry.name),name=prefix+entry.name;if(entry.isDirectory())add(full,name+'/');else if(entry.isFile())zip.file(name,fs.readFileSync(full));}}add(folder);fs.writeFileSync(filename,await zip.generateAsync({type:'nodebuffer',compression:'DEFLATE',compressionOptions:{level:6}}));console.log(filename);}
await packageFolder(path.join(root,'local-app'),path.join(root,'..','English-Garden-App.zip'),new Set(['data']));
await packageFolder(root,path.join(root,'..','English-Garden-Source.zip'),new Set(['node_modules','.git','.sites-runtime','.wrangler','.vinext','.next','dist','work','data','tsconfig.tsbuildinfo']));
