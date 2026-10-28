
const BASE = (import.meta.env.VITE_API_BASE_URL || 'https://relay-api-backend-2026.onrender.com/api').replace(/\/+$/, '');

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(BASE + path, {
      credentials: 'include',
      headers: {'Content-Type': 'application/json', ...(options.headers || {})},
      ...options
    });
  } catch (error) {
    throw new Error(`Cannot reach the RELAY server at ${BASE}. Check that Flask is running on port 5000.`);
  }

  let data = {};
  try { data = await res.json(); } catch {}
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}
export const api={
 health:()=>request('/health'),
 login:(email,password)=>request('/auth/login',{method:'POST',body:JSON.stringify({email,password})}),
 register:(payload)=>request('/auth/register',{method:'POST',body:JSON.stringify(payload)}),
 me:()=>request('/auth/me'), logout:()=>request('/auth/logout',{method:'POST'}),
 resources:(params='')=>request('/resources'+params), resource:(id)=>request('/resources/'+id), saveResource:(id,payload)=>request('/resources'+(id?'/'+id:''),{method:id?'PUT':'POST',body:JSON.stringify(payload)}), deleteResource:(id)=>request('/resources/'+id,{method:'DELETE'}),
 bookings:()=>request('/bookings'), booking:(id)=>request('/bookings/'+id), createBooking:(payload)=>request('/bookings',{method:'POST',body:JSON.stringify(payload)}), action:(id,a,payload={})=>request(`/bookings/${id}/${a}`,{method:'POST',body:JSON.stringify(payload)}),
 dashboard:(role)=>request('/dashboard/'+role), incidents:()=>request('/incidents'), incident:(payload)=>request('/incidents',{method:'POST',body:JSON.stringify(payload)}), incidentAction:(id,a,payload={})=>request(`/incidents/${id}/${a}`,{method:'POST',body:JSON.stringify(payload)}), audit:()=>request('/audit-logs')
}
