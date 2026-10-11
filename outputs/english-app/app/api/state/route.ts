import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '../../chatgpt-auth';
import { validState } from '../../model';
import { sameOrigin } from '../guard';
export async function GET() {
  const user = await getChatGPTUser();
  if (!user) return Response.json({ error: 'Bạn cần đăng nhập để lưu dữ liệu.' }, { status: 401 });
  const row = await env.DB!.prepare('SELECT data, revision, updated_at FROM learning_states WHERE user_id = ?').bind(user.userId).first<{data:string;revision:number;updated_at:string}>();
  return Response.json({ data: row ? JSON.parse(row.data) : null, revision: row?.revision ?? 0, updatedAt: row?.updated_at ?? null }, { headers: { 'Cache-Control': 'no-store' } });
}
export async function POST(request: Request) {
  if (!sameOrigin(request)) return Response.json({error:'Nguồn yêu cầu không hợp lệ.'},{status:403});
  const user = await getChatGPTUser();
  if (!user) return Response.json({error:'Bạn cần đăng nhập.'}, {status:401});
  const raw = await request.text();
  if (new TextEncoder().encode(raw).byteLength > 1_800_000) return Response.json({error:'Dữ liệu trên bản cloud vượt 1,8 MB. Sao lưu rồi rút gọn văn bản tài liệu; tệp gốc được lưu riêng.'},{status:413});
  let body;
  try { body = JSON.parse(raw); } catch { return Response.json({error:'Dữ liệu không hợp lệ.'},{status:400}); }
  const data = body.data;
  if (!validState(data) || !Number.isInteger(body.revision) || body.revision < 0) return Response.json({error:'Cấu trúc dữ liệu không hợp lệ.'},{status:400});
  const now = new Date().toISOString();
  let result;
  if (body.revision === 0) result = await env.DB!.prepare('INSERT OR IGNORE INTO learning_states (user_id,data,revision,updated_at) VALUES (?,?,1,?)').bind(user.userId,JSON.stringify(data),now).run();
  else result = await env.DB!.prepare('UPDATE learning_states SET data=?,revision=revision+1,updated_at=? WHERE user_id=? AND revision=?').bind(JSON.stringify(data),now,user.userId,body.revision).run();
  if (!result.meta.changes) return Response.json({error:'Dữ liệu đã thay đổi trên một cửa sổ khác. Sao lưu bản đang mở, sau đó tải lại trang.'},{status:409});
  return Response.json({revision:body.revision+1,updatedAt:now});
}
