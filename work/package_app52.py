from pathlib import Path
import zipfile,shutil,re,json
root=Path(__file__).resolve().parent.parent;app=root/'outputs/english-app';out=root/'outputs'
def pack(folder,target,skip):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as z:
        for p in folder.rglob('*'):
            relative=p.relative_to(folder)
            if any(x in skip or x.startswith('.env') for x in relative.parts):continue
            if p.is_file():z.write(p,relative.as_posix())
release=out/'English-Garden-App-v1.1-52-Tuan.zip'
pack(app/'local-app',release,{'data'})
shutil.copy2(release,out/'English-Garden-App.zip')
pack(app,out/'English-Garden-Source.zip',{'node_modules','.git','.sites-runtime','.wrangler','.vinext','.next','.openai','dist','build','work','data','tsconfig.tsbuildinfo'})
with zipfile.ZipFile(release) as z:
    names=z.namelist();assert 'MO-APP.cmd' in names and 'CAP-NHAT-V1.1.cmd' in names
    assert 'public/curriculum/Tieng-Anh-My-52-Tuan.pdf' in names
    assert not any(n.startswith('data/') for n in names)
    index=z.read('public/index.html').decode();assets=re.findall(r'(?:src|href)="(/assets/[^\"]+)"',index)
    assert all('public'+a in names for a in assets)
    js='\n'.join(z.read(n).decode('utf-8') for n in names if n.startswith('public/assets/index-') and n.endswith('.js'))
    assert 'us52-week-52' in js and 'us52-week-01' in js
print(json.dumps({'release':str(release),'bytes':release.stat().st_size,'files':len(names),'embeddedWeeks':52},ensure_ascii=False))
