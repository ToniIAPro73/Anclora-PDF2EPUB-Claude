-- Crear esquema privado si no existe (para objetos que no deben exponerse en la API) 
CREATE SCHEMA IF NOT EXISTS private;

-- Tabla de profiles en public 
CREATE TABLE IF NOT EXISTS public.profiles ( id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE, username text NOT NULL, full_name text, email text, avatar_url text, metadata jsonb, created_at timestamp with time zone DEFAULT now(), updated_at timestamp with time zone DEFAULT now() );

-- Índice para la columna foreign key user_id 
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);

-- Trigger function para mantener updated_at 
CREATE OR REPLACE FUNCTION public.set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN NEW.updated_at = now(); RETURN NEW; END; $$;

-- Trigger que usa la función 
DROP TRIGGER IF EXISTS trg_set_updated_at_profiles ON public.profiles; CREATE TRIGGER trg_set_updated_at_profiles BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Habilitar Row Level Security y crear políticas 
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policy: 
SELECT (solo el propio usuario) CREATE POLICY "Profiles select: owner only" ON public.profiles FOR SELECT TO authenticated USING ((SELECT auth.uid())::uuid = user_id);

-- Policy: 
INSERT (solo insertar usando su propio user_id) CREATE POLICY "Profiles insert: owner only" ON public.profiles FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid())::uuid = user_id);

-- Policy: 
UPDATE (solo modificar sus propias filas) CREATE POLICY "Profiles update: owner only" ON public.profiles FOR UPDATE TO authenticated USING ((SELECT auth.uid())::uuid = user_id) WITH CHECK ((SELECT auth.uid())::uuid = user_id);

-- Policy: 
DELETE (solo eliminar sus propias filas) CREATE POLICY "Profiles delete: owner only" ON public.profiles FOR DELETE TO authenticated USING ((SELECT auth.uid())::uuid = user_id);

-- Tabla de auditoría en esquema private 
CREATE TABLE IF NOT EXISTS private.profile_audit ( audit_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, profile_id bigint NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE, action text NOT NULL, -- e.g., INSERT, UPDATE, DELETE performed_by uuid, -- auth user id (if available) changes jsonb, created_at timestamp with time zone DEFAULT now() );

-- Índice para auditoría por profile_id 
CREATE INDEX IF NOT EXISTS idx_profile_audit_profile_id ON private.profile_audit(profile_id);

-- Trigger function para insertar en profile_audit al insertar/actualizar/eliminar en profiles 
CREATE OR REPLACE FUNCTION private.log_profile_changes() 
  RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE actor uuid := NULL;
BEGIN -- intentar capturar auth.uid() si existe en contexto; puede ser NULL en acciones internas BEGIN actor := (SELECT auth.uid()); EXCEPTION WHEN OTHERS THEN actor := NULL; END;
IF TG_OP = 'INSERT' THEN 
  INSERT INTO private.profile_audit(profile_id, action, performed_by, changes) VALUES (NEW.id, 'INSERT', actor, to_jsonb(NEW)); 
  RETURN NEW;
ELSIF TG_OP = 'UPDATE' THEN 
  INSERT INTO private.profile_audit(profile_id, action, performed_by, changes) VALUES (NEW.id, 'UPDATE', actor, jsonb_build_object('old', to_jsonb(OLD), 'new', to_jsonb(NEW))); 
  RETURN NEW; 
ELSIF TG_OP = 'DELETE' THEN 
  INSERT INTO private.profile_audit(profile_id, action, performed_by, changes) VALUES (OLD.id, 'DELETE', actor, to_jsonb(OLD)); 
  RETURN OLD; 
END IF; 
RETURN NULL; 
END; 
$$;

-- Asociar trigger de auditoría 
DROP TRIGGER IF EXISTS trg_profile_audit ON public.profiles; 
CREATE TRIGGER trg_profile_audit AFTER INSERT OR UPDATE OR DELETE ON public.profiles FOR EACH ROW EXECUTE FUNCTION private.log_profile_changes();

-- Nota de seguridad (texto en SQL como comentario) 
-- IMPORTANTE: La tabla private.profile_audit está en el esquema private para reducir su exposición desde la API. 
-- Las materialized views y tablas privadas deben mantenerse fuera de public porque RLS no se aplica automáticamente a objetos que permitan bypass. 
-- Para más detalles sobre riesgos ver: https://supabase.com/docs/guides/database/database-advisors?queryGroups=lint&lint=0016_materialized_view_in_api 
-- (El link anterior es para referencia de riesgo y auditoría de seguridad.)