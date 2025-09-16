-- =====================================================
-- Sistema de Créditos para Anclora PDF2EPUB
-- =====================================================

-- 1. Extender tabla profiles con créditos y referidos
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS credits integer DEFAULT 100;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS total_earned_credits integer DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS phone text;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS phone_verified boolean DEFAULT false;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS referral_code text UNIQUE;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS referred_by text;

-- 2. Tabla de transacciones de créditos
CREATE TABLE IF NOT EXISTS public.credit_transactions (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  amount integer NOT NULL, -- Positivo: ganado, Negativo: gastado
  transaction_type text NOT NULL CHECK (transaction_type IN ('initial_bonus', 'conversion_cost', 'referral_bonus', 'admin_adjustment')),
  conversion_id text, -- ID de conversión si aplica
  pipeline_id text, -- Pipeline usado
  description text,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- 3. Tabla de códigos de invitación y referidos
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

-- 4. Tabla de configuración de costos por pipeline
CREATE TABLE IF NOT EXISTS public.pipeline_costs (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  pipeline_id text NOT NULL UNIQUE,
  base_cost integer NOT NULL, -- Costo base del pipeline
  cost_per_page integer NOT NULL DEFAULT 0, -- Costo adicional por página
  quality_multiplier numeric(3,2) NOT NULL DEFAULT 1.0,
  description text,
  active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- 5. Índices para optimización
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON public.referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referral_code ON public.referrals(referral_code);
CREATE INDEX IF NOT EXISTS idx_profiles_referral_code ON public.profiles(referral_code);

-- 6. Función para generar código de referido único
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
    -- Generar código de 8 caracteres alfanuméricos
    code := upper(substr(md5(random()::text), 1, 8));

    -- Verificar que no existe
    SELECT EXISTS(SELECT 1 FROM public.profiles WHERE referral_code = code) INTO exists;

    EXIT WHEN NOT exists;
  END LOOP;

  RETURN code;
END;
$$;

-- 7. Trigger para generar código de referido automáticamente
CREATE OR REPLACE FUNCTION public.set_referral_code()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Solo generar si no tiene código de referido
  IF NEW.referral_code IS NULL THEN
    NEW.referral_code := public.generate_referral_code();
  END IF;

  RETURN NEW;
END;
$$;

-- Crear trigger
DROP TRIGGER IF EXISTS trg_set_referral_code ON public.profiles;
CREATE TRIGGER trg_set_referral_code
  BEFORE INSERT ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.set_referral_code();

-- 8. Función para calcular costo de conversión
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
  -- Obtener costos del pipeline
  SELECT pc.base_cost, pc.cost_per_page
  INTO base_cost, cost_per_page
  FROM public.pipeline_costs pc
  WHERE pc.pipeline_id = p_pipeline_id AND pc.active = true;

  -- Si no se encuentra el pipeline, usar costos por defecto
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

-- 9. Función para procesar transacción de créditos
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
  -- Obtener créditos actuales
  SELECT credits INTO current_credits
  FROM public.profiles
  WHERE user_id = p_user_id;

  -- Verificar que el usuario existe
  IF current_credits IS NULL THEN
    RAISE EXCEPTION 'Usuario no encontrado';
  END IF;

  -- Verificar saldo suficiente para transacciones negativas
  IF p_amount < 0 AND current_credits < ABS(p_amount) THEN
    RAISE EXCEPTION 'Saldo insuficiente. Créditos actuales: %, Requeridos: %', current_credits, ABS(p_amount);
  END IF;

  -- Insertar transacción
  INSERT INTO public.credit_transactions (
    user_id, amount, transaction_type, conversion_id,
    pipeline_id, description, metadata
  ) VALUES (
    p_user_id, p_amount, p_transaction_type, p_conversion_id,
    p_pipeline_id, p_description, p_metadata
  );

  -- Actualizar créditos del usuario
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

-- 10. Insertar configuración de costos por defecto
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

-- 11. RLS (Row Level Security) para las nuevas tablas
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_costs ENABLE ROW LEVEL SECURITY;

-- Políticas para credit_transactions
CREATE POLICY "Users can view own credit transactions" ON public.credit_transactions
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

-- Políticas para referrals
CREATE POLICY "Users can view own referrals" ON public.referrals
  FOR SELECT TO authenticated
  USING (referrer_id = auth.uid() OR referred_id = auth.uid());

CREATE POLICY "Users can insert own referrals" ON public.referrals
  FOR INSERT TO authenticated
  WITH CHECK (referrer_id = auth.uid());

-- Políticas para pipeline_costs (solo lectura para usuarios)
CREATE POLICY "Anyone can view pipeline costs" ON public.pipeline_costs
  FOR SELECT TO authenticated
  USING (active = true);

-- 12. Función para obtener balance de usuario
CREATE OR REPLACE FUNCTION public.get_user_credit_balance(p_user_id uuid)
RETURNS TABLE(
  current_credits integer,
  total_earned integer,
  total_spent integer,
  total_transactions bigint
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.credits,
    p.total_earned_credits,
    COALESCE(ABS(SUM(CASE WHEN ct.amount < 0 THEN ct.amount ELSE 0 END)), 0)::integer as total_spent,
    COUNT(ct.id) as total_transactions
  FROM public.profiles p
  LEFT JOIN public.credit_transactions ct ON ct.user_id = p.user_id
  WHERE p.user_id = p_user_id
  GROUP BY p.credits, p.total_earned_credits;
END;
$$;

-- Comentarios para documentación
COMMENT ON TABLE public.credit_transactions IS 'Registro de todas las transacciones de créditos de usuarios';
COMMENT ON TABLE public.referrals IS 'Sistema de referidos e invitaciones';
COMMENT ON TABLE public.pipeline_costs IS 'Configuración de costos por tipo de pipeline';
COMMENT ON FUNCTION public.calculate_conversion_cost IS 'Calcula el costo de una conversión basado en pipeline y páginas';
COMMENT ON FUNCTION public.process_credit_transaction IS 'Procesa una transacción de créditos de forma segura';