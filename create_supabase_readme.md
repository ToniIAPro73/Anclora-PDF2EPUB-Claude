-- File: create_supabase_readme.md

-- README: create_supabase_readme.md

# Supabase schema, RLS policies, and Edge Function

## What this package contains

- create_supabase_tables.sql: SQL to create public.profiles, RLS policies, indexes, trigger, and private.profile_audit.
- create-admin-user Edge Function: TypeScript (Deno) function to create auth users using the Service Role Key and insert a profile row.

## SQL summary

- public.profiles: stores public profile data and links to auth.users via user_id UUID foreign key.
- RLS: enabled on public.profiles with policies for SELECT/INSERT/UPDATE/DELETE restricted to the row owner via (SELECT auth.uid())::uuid = user_id.
- Indexes: created for user_id and audit table.
- Trigger: set_updated_at to keep updated_at timestamp current.
- private.profile_audit: audit table stored in private schema to reduce exposure via API.

## Edge Function: create-admin-user

Purpose:
- Create an auth user with the Admin API using the SUPABASE_SERVICE_ROLE_KEY.
- Insert a matching row into public.profiles with user_id set to the created user's id.
- Rollback (delete auth user) if profile insertion fails.

Deployment:
1. Save the Edge Function code as `create-admin-user/index.ts` in your project functions folder.
2. Deploy with the Supabase CLI or Dashboard. The environment variables SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are available in both local and hosted environments.

Example invocation (curl):

curl -X POST "<PROJECT_FUNCTIONS_URL>/create-admin-user" \
  -H "Content-Type: application/json" \
  -H "apikey: <SERVICE_ROLE_KEY>" \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>" \
  -d '{"email":"antonio@anclora.com","password":"ancloraadm","username":"anclora_admin","full_name":"Antonio"}'

## SQL execution and testing

1. Run the SQL file in the SQL editor or via psql. Example:
   psql $SUPABASE_DB_URL -f create_supabase_tables.sql

2. Confirm RLS policies exist and test as different users:
   - As anon: should not see other users' profiles.
   - As authenticated user A: can SELECT/INSERT/UPDATE/DELETE only their profile.

## Notes & recommendations

- Keep SUPABASE_SERVICE_ROLE_KEY secret.
- Revoke EXECUTE on any SECURITY DEFINER helper functions from anon/authenticated (none created here).
- Consider using `id uuid PRIMARY KEY` for profiles if you want profiles.id to equal auth.users.id. Current design keeps separate bigint id for profile records and user_id uuid FK.
- Add policies for admin/service_role roles if you need cross-user admin operations.

## Appendix: Full Edge Function code

(See create-admin-user/index.ts)