-- Supabase Setup Script for Anclora PDF2EPUB
-- This script creates the necessary tables and configures Row Level Security

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create conversions table
CREATE TABLE IF NOT EXISTS public.conversions (
    id BIGSERIAL PRIMARY KEY,
    task_id UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    input_filename VARCHAR(255),
    output_path VARCHAR(255),
    thumbnail_path VARCHAR(255),
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversions_user_id ON public.conversions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversions_task_id ON public.conversions(task_id);
CREATE INDEX IF NOT EXISTS idx_conversions_status ON public.conversions(status);
CREATE INDEX IF NOT EXISTS idx_conversions_created_at ON public.conversions(created_at);

-- Enable Row Level Security
ALTER TABLE public.conversions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for conversions
-- Users can only see their own conversions
CREATE POLICY "Users can view their own conversions" ON public.conversions
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own conversions
CREATE POLICY "Users can insert their own conversions" ON public.conversions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own conversions
CREATE POLICY "Users can update their own conversions" ON public.conversions
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own conversions
CREATE POLICY "Users can delete their own conversions" ON public.conversions
    FOR DELETE USING (auth.uid() = user_id);

-- Create a function to automatically update the updated_at column
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER handle_conversions_updated_at
    BEFORE UPDATE ON public.conversions
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Create a view for conversion statistics (optional)
CREATE OR REPLACE VIEW public.conversion_stats AS
SELECT 
    user_id,
    COUNT(*) as total_conversions,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_conversions,
    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_conversions,
    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_conversions,
    MAX(created_at) as last_conversion_date
FROM public.conversions
GROUP BY user_id;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.conversions TO authenticated;
GRANT SELECT ON public.conversion_stats TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
