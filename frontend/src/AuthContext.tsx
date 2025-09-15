import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useRef,
} from 'react';
import { supabase } from './lib/supabase';
import type { User, Session } from '@supabase/supabase-js';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshTimer = useRef<NodeJS.Timeout | null>(null);

  const scheduleRefresh = (currentSession: Session | null) => {
    if (refreshTimer.current) {
      clearTimeout(refreshTimer.current);
    }
    const expiresAt = currentSession?.expires_at ? currentSession.expires_at * 1000 : null;
    if (expiresAt) {
      const timeout = Math.max(expiresAt - Date.now() - 60_000, 0);
      refreshTimer.current = setTimeout(refreshSession, timeout);
    }
  };

  const refreshSession = async () => {
    try {
      const { data, error } = await supabase.auth.refreshSession();
      if (error) throw error;
      const newSession = data.session;
      setSession(newSession);
      setUser(newSession?.user ?? null);
      setToken(newSession?.access_token ?? null);
      scheduleRefresh(newSession);
    } catch (err) {
      console.error('Error refreshing session', err);
      try {
        const { data } = await supabase.auth.getSession();
        const newSession = data.session;
        if (newSession) {
          setSession(newSession);
          setUser(newSession.user);
          setToken(newSession.access_token);
          scheduleRefresh(newSession);
          return;
        }
      } catch (_) {
        // Ignore secondary error
      }
      await supabase.auth.signOut();
      setUser(null);
      setSession(null);
      setToken(null);
      alert('Tu sesión ha expirado. Por favor, inicia sesión de nuevo.');
    }
  };

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setToken(session?.access_token ?? null);
      setLoading(false);
      scheduleRefresh(session);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setToken(session?.access_token ?? null);
      setLoading(false);
      scheduleRefresh(session);
    });

    return () => {
      subscription.unsubscribe();
      if (refreshTimer.current) {
        clearTimeout(refreshTimer.current);
      }
    };
  }, []);

  const login = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) {
      throw new Error(error.message);
    }
  };

  const register = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
    });
    if (error) {
      throw new Error(error.message);
    }
  };

  const logout = async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      throw new Error(error.message);
    }
  };

  const token = session?.access_token ?? null;

  return (
    <AuthContext.Provider value={{ user, session, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

