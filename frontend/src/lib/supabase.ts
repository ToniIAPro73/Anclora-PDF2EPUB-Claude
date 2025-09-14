import { createClient } from '@supabase/supabase-js'

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://kehpwxdkpdxapfxwhfwn.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlaHB3eGRrcGR4YXBmeHdoZnduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTU4NzgsImV4cCI6MjA2Njg3MTg3OH0.K8cs9gQWc1P6Js4q8H88QQyJ4Nh4CVbV4JW70QpjOlM'

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface User {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface Conversion {
  id: number
  task_id: string
  user_id: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  input_filename?: string
  output_path?: string
  thumbnail_path?: string
  metrics?: any
  created_at: string
  updated_at: string
}

// Note: user_id is actually a UUID from auth.users, but we keep it as string for TypeScript compatibility
