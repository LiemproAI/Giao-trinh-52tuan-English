import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '../../chatgpt-auth';
import { sameOrigin } from '../guard';
export async function POST(request: Request) {
  if(!sameOrigin(request))return Response.json({error:'Nguồn yêu cầu không hợp lệ.'},{status:403});
  const user = await getChatGPTUser();
  if (!user) return Response.json({error:'Bạn cần đăng nhập.'},{status:401});
  if (Number(request.headers.get('content-length') || 0) > 21_000_000) return Response.json({error:'Tệp tối đa 20 MB.'},{status:413});
  const form = await request.formData(); const file = form.get('file');
  if (!(file instanceof File) || file.size > 20_000_000) return Response.json({error:'Tệp tối đa 20 MB.'},{status:400});
  if (!/\.(pdf|docx?|txt|csv|tsv|json|webm|wav|mp4|m4a|ogg)$/i.test(file.name)) return Response.json({error:'Định dạng tệp chưa hỗ trợ.'},{status:400});
  const id = crypto.randomUUID();
  await env.BUCKET!.put(`${user.userId}/${id}`, await file.arrayBuffer(), {httpMetadata:{contentType:'application/octet-stream'},customMetadata:{name:file.name}});
  return Response.json({id,name:file.name,size:file.size});
}
export async function GET(request: Request) {
  const user = await getChatGPTUser(); if (!user) return new Response('Unauthorized',{status:401});
  const id = new URL(request.url).searchParams.get('id') || '';
  if (!/^[a-f0-9-]{36}$/.test(id)) return new Response('Invalid id',{status:400});
  const file = await env.BUCKET!.get(`${user.userId}/${id}`); if (!file) return new Response('Not found',{status:404});
  return new Response(file.body, {headers:{'Content-Type':'application/octet-stream','Content-Disposition':`attachment; filename*=UTF-8''${encodeURIComponent(file.customMetadata?.name || 'file')}`,'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
}
export async function DELETE(request: Request) {
 if(!sameOrigin(request))return new Response('Forbidden',{status:403});
 const user=await getChatGPTUser(); if(!user) return new Response('Unauthorized',{status:401});
 const id=new URL(request.url).searchParams.get('id')||''; if(!/^[a-f0-9-]{36}$/.test(id))return new Response('Invalid id',{status:400});
 await env.BUCKET!.delete(`${user.userId}/${id}`);return Response.json({ok:true});
}
