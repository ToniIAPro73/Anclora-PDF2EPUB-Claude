-- =====================================================
-- MIGRACIÓN INCREMENTAL - Sistema de Créditos
-- Solo agrega lo que falta, respeta lo existente
-- =====================================================

-- 1. EXTENDER TABLA PROFILES (solo agregar columnas nuevas)
DO $$
BEGIN
    -- Agregar columnas de créditos solo si no existen
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='credits') THEN
        ALTER TABLE public.profiles ADD COLUMN credits integer DEFAULT 100;
        RAISE NOTICE 'Columna credits agregada a profiles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='total_earned_credits') THEN
        ALTER TABLE public.profiles ADD COLUMN total_earned_credits integer DEFAULT 0;
        RAISE NOTICE 'Columna total_earned_credits agregada a profiles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='phone') THEN
        ALTER TABLE public.profiles ADD COLUMN phone text;
        RAISE NOTICE 'Columna phone agregada a profiles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='phone_verified') THEN
        ALTER TABLE public.profiles ADD COLUMN phone_verified boolean DEFAULT false;
        RAISE NOTICE 'Columna phone_verified agregada a profiles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='referral_code') THEN
        ALTER TABLE public.profiles ADD COLUMN referral_code text UNIQUE;
        RAISE NOTICE 'Columna referral_code agregada a profiles';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='referred_by') THEN
        ALTER TABLE public.profiles ADD COLUMN referred_by text;
        RAISE NOTICE 'Columna referred_by agregada a profiles';
    END IF;
END $$;

-- 2. EXTENDER TABLA CONVERSIONS (solo agregar columnas nuevas)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversions' AND column_name='user_id') THEN
        ALTER TABLE public.conversions ADD COLUMN user_id uuid;
        RAISE NOTICE 'Columna user_id agregada a conversions';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversions' AND column_name='pipeline_id') THEN
        ALTER TABLE public.conversions ADD COLUMN pipeline_id text;
        RAISE NOTICE 'Columna pipeline_id agregada a conversions';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversions' AND column_name='credits_cost') THEN
        ALTER TABLE public.conversions ADD COLUMN credits_cost integer DEFAULT 0;
        RAISE NOTICE 'Columna credits_cost agregada a conversions';
    END IF;
END $$;

-- 3. CREAR NUEVAS TABLAS (solo si no existen)
CREATE TABLE IF NOT EXISTS public.credit_transactions (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  amount integer NOT NULL,
  transaction_type text NOT NULL CHECK (transaction_type IN ('initial_bonus', 'conversion_cost', 'referral_bonus', 'admin_adjustment')),
  conversion_id text,
  pipeline_id text,
  description text,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.referrals (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  referrer_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  referred_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  referral_code text NOT NULL,
  email_invited text,
  phone_invited text,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'verified', 'expired')),
  credits_awarded_referrer integer DEFAULT 0,
  credits_awarded_referred integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS public.pipeline_costs (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  pipeline_id text NOT NULL UNIQUE,
  base_cost integer NOT NULL,
  cost_per_page integer NOT NULL DEFAULT 0,
  quality_multiplier numeric(3,2) NOT NULL DEFAULT 1.0,
  description text,
  active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- 4. CREAR ÍNDICES (solo si no existen)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_credit_transactions_user_id') THEN
        CREATE INDEX idx_credit_transactions_user_id ON public.credit_transactions(user_id);
        RAISE NOTICE 'Índice idx_credit_transactions_user_id creado';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_credit_transactions_created_at') THEN
        CREATE INDEX idx_credit_transactions_created_at ON public.credit_transactions(created_at);
        RAISE NOTICE 'Índice idx_credit_transactions_created_at creado';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_referrals_referrer_id') THEN
        CREATE INDEX idx_referrals_referrer_id ON public.referrals(referrer_id);
        RAISE NOTICE 'Índice idx_referrals_referrer_id creado';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_referrals_referral_code') THEN
        CREATE INDEX idx_referrals_referral_code ON public.referrals(referral_code);
        RAISE NOTICE 'Índice idx_referrals_referral_code creado';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_profiles_referral_code') THEN
        CREATE INDEX idx_profiles_referral_code ON public.profiles(referral_code);
        RAISE NOTICE 'Índice idx_profiles_referral_code creado';
    END IF;
END $$;

-- 5. CREAR FUNCIONES (reemplazar si existen)
CREATE OR REPLACE FUNCTION public.generate_referral_code()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  code text;
  exists boolean;
BEGIN
  LOOP
    code := upper(substr(md5(random()::text), 1, 8));
    SELECT EXISTS(SELECT 1 FROM public.profiles WHERE referral_code = code) INTO exists;
    EXIT WHEN NOT exists;
  END LOOP;
  RETURN code;
END;
$$;

CREATE OR REPLACE FUNCTION public.set_referral_code()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  IF NEW.referral_code IS NULL THEN
    NEW.referral_code := public.generate_referral_code();
  END IF;
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.calculate_conversion_cost(
  p_pipeline_id text,
  p_page_count integer DEFAULT 1
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  base_cost integer;
  cost_per_page integer;
  total_cost integer;
BEGIN
  SELECT pc.base_cost, pc.cost_per_page
  INTO base_cost, cost_per_page
  FROM public.pipeline_costs pc
  WHERE pc.pipeline_id = p_pipeline_id AND pc.active = true;

  IF base_cost IS NULL THEN
    CASE p_pipeline_id
      WHEN 'engines.low' THEN
        base_cost := 1;
        cost_per_page := 0;
      WHEN 'engines.medium' THEN
        base_cost := 3;
        cost_per_page := 1;
      WHEN 'engines.high' THEN
        base_cost := 8;
        cost_per_page := 2;
      ELSE
        base_cost := 5;
        cost_per_page := 1;
    END CASE;
  END IF;

  total_cost := base_cost + (cost_per_page * GREATEST(p_page_count - 1, 0));
  RETURN total_cost;
END;
$$;

CREATE OR REPLACE FUNCTION public.process_credit_transaction(
  p_user_id uuid,
  p_amount integer,
  p_transaction_type text,
  p_conversion_id text DEFAULT NULL,
  p_pipeline_id text DEFAULT NULL,
  p_description text DEFAULT NULL,
  p_metadata jsonb DEFAULT NULL
)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_credits integer;
BEGIN
  SELECT credits INTO current_credits
  FROM public.profiles
  WHERE user_id = p_user_id;

  IF current_credits IS NULL THEN
    RAISE EXCEPTION 'Usuario no encontrado';
  END IF;

  IF p_amount < 0 AND current_credits < ABS(p_amount) THEN
    RAISE EXCEPTION 'Saldo insuficiente. Créditos actuales: %, Requeridos: %', current_credits, ABS(p_amount);
  END IF;

  INSERT INTO public.credit_transactions (
    user_id, amount, transaction_type, conversion_id,
    pipeline_id, description, metadata
  ) VALUES (
    p_user_id, p_amount, p_transaction_type, p_conversion_id,
    p_pipeline_id, p_description, p_metadata
  );

  UPDATE public.profiles
  SET
    credits = credits + p_amount,
    total_earned_credits = CASE
      WHEN p_amount > 0 THEN total_earned_credits + p_amount
      ELSE total_earned_credits
    END,
    updated_at = now()
  WHERE user_id = p_user_id;

  RETURN true;
END;
$$;

-- 6. CREAR TRIGGER (solo si no existe)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_set_referral_code') THEN
        CREATE TRIGGER trg_set_referral_code
          BEFORE INSERT ON public.profiles
          FOR EACH ROW
          EXECUTE FUNCTION public.set_referral_code();
        RAISE NOTICE 'Trigger trg_set_referral_code creado';
    END IF;
END $$;

-- 7. HABILITAR RLS EN NUEVAS TABLAS
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_costs ENABLE ROW LEVEL SECURITY;

-- 8. CREAR POLÍTICAS RLS (solo si no existen)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own credit transactions') THEN
        CREATE POLICY "Users can view own credit transactions" ON public.credit_transactions
          FOR SELECT TO authenticated
          USING (user_id = auth.uid());
        RAISE NOTICE 'Política credit_transactions creada';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view own referrals') THEN
        CREATE POLICY "Users can view own referrals" ON public.referrals
          FOR SELECT TO authenticated
          USING (referrer_id = auth.uid() OR referred_id = auth.uid());
        RAISE NOTICE 'Política referrals SELECT creada';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can insert own referrals') THEN
        CREATE POLICY "Users can insert own referrals" ON public.referrals
          FOR INSERT TO authenticated
          WITH CHECK (referrer_id = auth.uid());
        RAISE NOTICE 'Política referrals INSERT creada';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Anyone can view pipeline costs') THEN
        CREATE POLICY "Anyone can view pipeline costs" ON public.pipeline_costs
          FOR SELECT TO authenticated
          USING (active = true);
        RAISE NOTICE 'Política pipeline_costs creada';
    END IF;
END $$;

-- 9. INSERTAR DATOS INICIALES DE COSTOS
INSERT INTO public.pipeline_costs (pipeline_id, base_cost, cost_per_page, description)
VALUES
  ('engines.low', 1, 0, 'Pipeline rápido - Calidad básica'),
  ('engines.medium', 3, 1, 'Pipeline equilibrado - Calidad media'),
  ('engines.high', 8, 2, 'Pipeline de calidad - Máxima calidad')
ON CONFLICT (pipeline_id) DO UPDATE SET
  base_cost = EXCLUDED.base_cost,
  cost_per_page = EXCLUDED.cost_per_page,
  description = EXCLUDED.description,
  updated_at = now();

-- 10. OTORGAR CRÉDITOS INICIALES A USUARIOS EXISTENTES (si no los tienen)
DO $$
DECLARE
    user_record RECORD;
BEGIN
    FOR user_record IN
        SELECT user_id FROM public.profiles
        WHERE credits IS NULL OR credits = 0
    LOOP
        UPDATE public.profiles
        SET
            credits = 100,
            total_earned_credits = 100,
            updated_at = now()
        WHERE user_id = user_record.user_id;

        INSERT INTO public.credit_transactions (
            user_id, amount, transaction_type, description
        ) VALUES (
            user_record.user_id,
            100,
            'initial_bonus',
            'Créditos de bienvenida - Migración del sistema'
        );

        RAISE NOTICE 'Créditos iniciales otorgados a usuario: %', user_record.user_id;
    END LOOP;
END $$;

-- =====================================================
-- RESUMEN FINAL
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '✅ MIGRACIÓN INCREMENTAL COMPLETADA';
    RAISE NOTICE '📊 Sistema de créditos activado';
    RAISE NOTICE '🎁 Usuarios existentes recibieron 100 créditos';
    RAISE NOTICE '🚀 Backend listo para usar las nuevas APIs';
END
$$;