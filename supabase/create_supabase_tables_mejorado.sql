-- Correcciones y mejoras al SQL original: creación de esquema privado, tabla de profiles, triggers, RLS y auditoría

-- 1) Crear esquema private si no existe
CREATE SCHEMA IF NOT EXISTS private;

-- 2) Tabla de profiles en public
CREATE TABLE IF NOT EXISTS public.profiles (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  full_name text,
  email text,
  avatar_url text,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Índice para la columna foreign key user_id
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);

-- 3) Trigger function para mantener updated_at
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Asegurarse de que el trigger exista y esté asociado
DROP TRIGGER IF EXISTS trg_set_updated_at_profiles ON public.profiles;
CREATE TRIGGER trg_set_updated_at_profiles
BEFORE UPDATE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- 4) Habilitar Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 5) Políticas RLS corregidas
-- SELECT: solo el propio usuario puede leer su perfil
CREATE POLICY "Profiles select: owner only" ON public.profiles
  FOR SELECT
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id);

-- INSERT: solo puede insertar con su propio user_id
CREATE POLICY "Profiles insert: owner only" ON public.profiles
  FOR INSERT
  TO authenticated
  WITH CHECK ((SELECT auth.uid())::uuid = user_id);

-- UPDATE: solo puede modificar sus propias filas
CREATE POLICY "Profiles update: owner only" ON public.profiles
  FOR UPDATE
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id)
  WITH CHECK ((SELECT auth.uid())::uuid = user_id);

-- DELETE: solo puede eliminar sus propias filas
CREATE POLICY "Profiles delete: owner only" ON public.profiles
  FOR DELETE
  TO authenticated
  USING ((SELECT auth.uid())::uuid = user_id);

-- 6) Tabla de auditoría en esquema private
CREATE TABLE IF NOT EXISTS private.profile_audit (
  audit_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  profile_id bigint NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  action text NOT NULL,
  performed_by uuid,
  changes jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Índice para auditoría por profile_id
CREATE INDEX IF NOT EXISTS idx_profile_audit_profile_id ON private.profile_audit(profile_id);

-- 7) Trigger function para insertar en profile_audit
CREATE OR REPLACE FUNCTION private.log_profile_changes()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
  actor uuid := NULL;
BEGIN
  -- intentar capturar auth.uid() si existe en contexto; puede ser NULL
  BEGIN
    actor := (SELECT auth.uid());
  EXCEPTION WHEN OTHERS THEN
    actor := NULL;
  END;

  IF TG_OP = 'INSERT' THEN
    INSERT INTO private.profile_audit(profile_id, action, performed_by, changes)
    VALUES (NEW.id, 'INSERT', actor, to_jsonb(NEW));
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO private.profile_audit(profile_id, action, performed_by, changes)
    VALUES (NEW.id, 'UPDATE', actor, jsonb_build_object('old', to_jsonb(OLD), 'new', to_jsonb(NEW)));
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO private.profile_audit(profile_id, action, performed_by, changes)
    VALUES (OLD.id, 'DELETE', actor, to_jsonb(OLD));
    RETURN OLD;
  END IF;

  RETURN NULL;
END;
$$;

-- Asociar trigger de auditoría
DROP TRIGGER IF EXISTS trg_profile_audit ON public.profiles;
CREATE TRIGGER trg_profile_audit
AFTER INSERT OR UPDATE OR DELETE ON public.profiles
FOR EACH ROW
EXECUTE FUNCTION private.log_profile_changes();

-- Nota de seguridad: La tabla private.profile_audit está en esquema private para reducir exposición desde la API.
-- Las materialized views y tablas privadas deben mantenerse fuera de public porque RLS no se aplica automáticamente a objetos que permitan bypass.