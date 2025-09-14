// functions/create-admin-user/index.ts

import { createClient } from "npm:@supabase/supabase-js@2.36.0";

console.info('create-admin-user function starting');

Deno.serve(async (req: Request) => { try { if (req.method !== 'POST') { return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: { 'Content-Type': 'application/json' } }); }

const supabaseUrl = Deno.env.get('SUPABASE_URL');
const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

if (!supabaseUrl || !serviceRoleKey) {
  return new Response(JSON.stringify({ error: 'Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY' }), { status: 500, headers: { 'Content-Type': 'application/json' } });
}

const body = await req.json().catch(() => null);
if (!body) {
  return new Response(JSON.stringify({ error: 'Invalid JSON body' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
}

const { email, password, username, full_name } = body;
if (!email || !password || !username) {
  return new Response(JSON.stringify({ error: 'Missing required fields: email, password, username' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
}

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: { persistSession: false },
});

// Crear el usuario Auth via Admin API
const { data: userData, error: userError } = await supabase.auth.admin.createUser({
  email: email,
  password: password,
  email_confirm: true,
  user_metadata: { username, full_name },
});

if (userError) {
  return new Response(JSON.stringify({ error: 'Auth user creation failed', details: userError }), { status: 500, headers: { 'Content-Type': 'application/json' } });
}

const createdUser = userData;
const userId = createdUser?.id;
if (!userId) {
  return new Response(JSON.stringify({ error: 'User created but no id returned' }), { status: 500, headers: { 'Content-Type': 'application/json' } });
}

// Insertar profile en public.profiles
const { data: profileData, error: profileError } = await supabase
  .from('profiles')
  .insert([{ user_id: userId, username, full_name, email }])
  .select()
  .single();

if (profileError) {
  // Intentar rollback: eliminar el usuario de Auth para evitar usuarios huérfanos
  try {
    await supabase.auth.admin.deleteUser(userId);
  } catch (e) {
    console.warn('Failed to rollback created user', e);
  }
  return new Response(JSON.stringify({ error: 'Profile creation failed', details: profileError }), { status: 500, headers: { 'Content-Type': 'application/json' } });
}

return new Response(JSON.stringify({ user: createdUser, profile: profileData }), { status: 201, headers: { 'Content-Type': 'application/json' } });

} catch (err) { console.error('Unhandled error in function', err); return new Response(JSON.stringify({ error: 'Internal server error', details: String(err) }), { status: 500, headers: { 'Content-Type': 'application/json' } }); } });

