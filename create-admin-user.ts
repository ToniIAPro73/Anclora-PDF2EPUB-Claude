/*
  Edge Function: create-admin-user
  Descripción: Crea un usuario en Supabase Auth usando la Service Role Key y crea el profile
  correspondiente en public.profiles. Si la creación del profile falla, intenta eliminar
  el usuario de Auth para evitar usuarios huérfanos.

  Requisitos de entorno (predefinidos por Supabase hospedado):
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY

  Buenas prácticas:
  - Mantén SUPABASE_SERVICE_ROLE_KEY como secreto (no en control de versiones).
  - Proporciona esta función sólo a sistemas de confianza (solo llamadas con la service role key).
*/

import { createClient } from "npm:@supabase/supabase-js@2.36.0";

// --- Tipos de entrada ---

// --- Utilidades internas ---
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

const getEnv = (key) => Deno.env.get(key) ?? null;

const initSupabase = () => {
  const supabaseUrl = getEnv("SUPABASE_URL");
  const serviceRoleKey = getEnv("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceRoleKey) return null;
  return createClient(supabaseUrl, serviceRoleKey, { auth: { persistSession: false } });
};

// Validación simple de email (no exhaustiva)
const isValidEmail = (email) => /@/.test(email) && email.length > 5;
// Validación de password mínima
const isValidPassword = (pw) => pw.length >= 8;
// Validación username
const isValidUsername = (u) => /^[a-zA-Z0-9_\-\.]{3,30}$/.test(u);

console.info("create-admin-user: starting");

Deno.serve(async (req) => {
  try {
    if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

    const supabase = initSupabase();
    if (!supabase)
      return json({ error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment" }, 500);

    // Leer body
    const payload = await req.json().catch(() => null);
    if (!payload) return json({ error: "Invalid or missing JSON body" }, 400);

    const { email, password, username, full_name, metadata } = payload;

    // Validaciones
    if (!email || !password || !username)
      return json({ error: "Missing required fields: email, password, username" }, 400);
    if (!isValidEmail(email)) return json({ error: "Invalid email format" }, 400);
    if (!isValidPassword(password)) return json({ error: "Password must be at least 8 characters" }, 400);
    if (!isValidUsername(username))
      return json({ error: "Invalid username: use 3-30 chars, letters, numbers, - _ . allowed" }, 400);

    // Evitar duplicados a nivel de profile (username o email) - la service role key permite leer la tabla
    // 1) comprobar username en public.profiles
    const { data: existingByUsername, error: errUsername } = await supabase
      .from("profiles")
      .select("id, user_id, username, email")
      .eq("username", username)
      .limit(1);

    if (errUsername) {
      console.error("Error checking username uniqueness", errUsername);
      return json({ error: "Internal error checking username" }, 500);
    }

    if (existingByUsername && existingByUsername.length > 0) return json({ error: "Username already exists" }, 409);

    // 2) comprobar email en profiles (si tu diseño almacena email en profiles)
    const { data: existingByEmail, error: errEmail } = await supabase
      .from("profiles")
      .select("id, user_id, username, email")
      .eq("email", email)
      .limit(1);

    if (errEmail) {
      console.error("Error checking email uniqueness", errEmail);
      return json({ error: "Internal error checking email" }, 500);
    }

    if (existingByEmail && existingByEmail.length > 0) return json({ error: "Email already in use" }, 409);

    // Crear usuario en Auth (admin)
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: { username, full_name, ...metadata },
    });

    if (authError) {
      console.error("Auth user creation failed", authError);
      return json({ error: "Auth user creation failed", details: authError }, 500);
    }

    const createdUser = authData; // contiene id y detalles del usuario
    const userId = createdUser?.id;
    if (!userId) {
      console.error("Auth created but returned no id", createdUser);
      return json({ error: "Auth created but no id returned" }, 500);
    }

    // Insertar profile en public.profiles (usando service_role_key para saltar RLS si fuese necesario)
    const profileRow = {
      user_id: userId,
      username,
      full_name: full_name ?? null,
      email,
      metadata: metadata ?? null,
    };

    const { data: profileData, error: profileError } = await supabase
      .from("profiles")
      .insert([profileRow])
      .select()
      .single();

    if (profileError) {
      console.error("Profile creation failed, attempting rollback", profileError);
      // Intentar rollback: eliminar usuario de Auth
      try {
        const { error: delErr } = await supabase.auth.admin.deleteUser(userId);
        if (delErr) console.error("Rollback: failed to delete auth user", delErr);
        else console.info("Rollback: deleted auth user", userId);
      } catch (e) {
        console.error("Rollback: exception deleting auth user", e);
      }

      return json({ error: "Profile creation failed, rolled back auth user if possible", details: profileError }, 500);
    }

    // Éxito: devolver el usuario (sin claves) y el profile
    // Nota: authData puede contener campos sensibles; sólo devolvemos id, email y user_metadata mínimos
    const safeUser = {
      id: createdUser.id,
      email: createdUser.email,
      user_metadata: createdUser.user_metadata,
      role: createdUser.role ?? null,
      created_at: createdUser.created_at ?? null,
    };

    // Respuesta 201 Created
    return json({ user: safeUser, profile: profileData }, 201);
  } catch (err) {
    console.error("Unhandled error in create-admin-user", err);
    return json({ error: "Internal server error", details: String(err) }, 500);
  }
});