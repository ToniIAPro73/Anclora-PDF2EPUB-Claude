import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabasePublishableKey)

// Database types
export interface Profile {
  id: number
  user_id: string
  username: string
  full_name?: string
  email: string
  avatar_url?: string
  metadata?: any
  created_at: string
  updated_at: string
}

export interface Conversion {
  id: number
  task_id: string
  user_id: string
  status: string
  input_filename?: string
  output_path?: string
  thumbnail_path?: string
  metrics?: any
  created_at: string
  updated_at: string
}

// Note: user_id is actually a UUID from auth.users, but we keep it as string for TypeScript compatibility
