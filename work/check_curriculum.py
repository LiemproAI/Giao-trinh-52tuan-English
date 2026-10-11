from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageDraw
import json,zipfile,csv,io
root=Path(__file__).resolve().parent.parent
pdfpath=root/'outputs/Tieng-Anh-My-52-Tuan.pdf'; reader=PdfReader(str(pdfpath))
assert len(reader.pages)==125
text='\n'.join(p.extract_text() for p in reader.pages)
assert all(f'Tuần {i:02d}' in text for i in range(1,53))
assert '\ufffd' not in text
z=zipfile.ZipFile(root/'outputs/Tu-Vung-52-Tuan.zip');assert len(z.namelist())==106
rows=list(csv.reader(io.StringIO(z.read('Tat-ca-312-cau.csv').decode('utf-8-sig'))));assert len(rows)==313
assert all(len(r)==2 for r in rows)
dest=root/'work/pdf-check';dest.mkdir(exist_ok=True)
doc=pdfium.PdfDocument(str(pdfpath))
thumbs=[]
for i in range(len(doc)):
    page=doc[i];im=page.render(scale=.45).to_pil().convert('RGB');thumbs.append(im)
    if i in [0,1,2,3,8,9,34,35,66,67,86,87,110,111,112,124]:
        page.render(scale=1.5).to_pil().save(dest/f'page-{i+1:03d}.png')
for start in range(0,len(thumbs),25):
    sheet=Image.new('RGB',(5*280,5*405),'#d5d5d5');d=ImageDraw.Draw(sheet)
    for j,im in enumerate(thumbs[start:start+25]):
        x=(j%5)*280;y=(j//5)*405;sheet.paste(im,(x+6,y+20));d.text((x+6,y+3),str(start+j+1),fill='black')
    sheet.save(dest/f'contact-{start//25+1}.png')
print(json.dumps({'pages':len(reader.pages),'csv_entries':len(rows)-1,'zip_files':len(z.namelist()),'text_chars':len(text),'rendered_pages':len(thumbs)}))
