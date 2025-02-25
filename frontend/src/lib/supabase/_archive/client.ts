import { createBrowserClient } from '@supabase/ssr'
import type { Session } from '@supabase/supabase-js'

// Declare environment variables
declare global {
  namespace App {
    interface Locals {
      getSession: () => Promise<Session | null>
    }
  }
  namespace NodeJS {
    interface ProcessEnv {
      PUBLIC_SUPABASE_URL: string
      PUBLIC_SUPABASE_ANON_KEY: string
    }
  }
}

export const createClient = () => {
  return createBrowserClient(
    process.env.PUBLIC_SUPABASE_URL,
    process.env.PUBLIC_SUPABASE_ANON_KEY
  )
} 