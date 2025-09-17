import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useRef,
  useCallback,
  useMemo,
} from "react";
import { supabase } from "./lib/supabase";
import type { User, Session } from "@supabase/supabase-js";
import i18n from "./i18n";
import Toast from "./components/Toast";
import { createAuthenticatedApi } from "./lib/apiClient";

/**
 * Authentication context type definition
 */
interface AuthContextType {
  user: User | null;
  session: Session | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  language: string;
  setLanguage: (lang: string) => void;
  api: ReturnType<typeof createAuthenticatedApi>;
}

// Toast configuration interface
interface ToastConfig {
  title: string;
  message: string;
  variant: "success" | "error" | "warning" | "info";
}

// Create context with undefined default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Token refresh configuration
const TOKEN_REFRESH_MARGIN = 5 * 60 * 1000; // 5 minutes before expiry
const TOKEN_REFRESH_MIN_INTERVAL = 10 * 1000; // Minimum 10 seconds between refresh attempts

/**
 * Authentication provider component
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // State management
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<ToastConfig | null>(null);
  
  // Language preference with localStorage persistence
  const [language, setLanguage] = useState<string>(() =>
    localStorage.getItem("language") ||
    localStorage.getItem("i18nextLng") ||
    "es"
  );
  
  // Reference for token refresh timer
  const refreshTimer = useRef<NodeJS.Timeout | null>(null);

  /**
   * Show a toast message with optional auto-dismiss
   */
  const showToast = useCallback((config: ToastConfig, autoDismiss = true) => {
    setToast(config);
    
    // Auto-dismiss success and info toasts after 5 seconds
    if (autoDismiss && (config.variant === 'success' || config.variant === 'info')) {
      setTimeout(() => setToast(null), 5000);
    }
  }, []);

  /**
   * Schedule token refresh before expiry
   */
  const scheduleRefresh = useCallback((currentSession: Session | null) => {
    // Clear any existing timer
    if (refreshTimer.current) {
      clearTimeout(refreshTimer.current);
      refreshTimer.current = null;
    }
    
    // Calculate when to refresh
    const expiresAt = currentSession?.expires_at ? currentSession.expires_at * 1000 : null;
    if (expiresAt) {
      // Refresh TOKEN_REFRESH_MARGIN before expiry, but not less than TOKEN_REFRESH_MIN_INTERVAL
      const timeout = Math.max(expiresAt - Date.now() - TOKEN_REFRESH_MARGIN, TOKEN_REFRESH_MIN_INTERVAL);
      console.info(`🔄 Token refresh scheduled in ${Math.round(timeout / 1000)} seconds`);
      refreshTimer.current = setTimeout(refreshSession, timeout);
    }
  }, []);

  /**
   * Refresh the authentication session
   */
  const refreshSession = useCallback(async () => {
    try {
      console.info("🔄 Refreshing authentication session...");
      const { data, error } = await supabase.auth.refreshSession();
      
      if (error) throw error;
      
      const newSession = data.session;
      setSession(newSession);
      setUser(newSession?.user ?? null);
      setToken(newSession?.access_token ?? null);
      scheduleRefresh(newSession);
      
      console.info("✅ Session refreshed successfully");
    } catch (err) {
      console.error("❌ Error refreshing session:", err);
      
      // Try to get the current session as a fallback
      try {
        const { data } = await supabase.auth.getSession();
        const newSession = data.session;
        
        if (newSession) {
          console.info("✅ Retrieved current session as fallback");
          setSession(newSession);
          setUser(newSession.user);
          setToken(newSession.access_token);
          scheduleRefresh(newSession);
          return;
        }
      } catch (fallbackError) {
        console.error("❌ Fallback session retrieval failed:", fallbackError);
      }
      
      // If all else fails, sign out
      console.warn("⚠️ Session refresh failed, signing out");
      await supabase.auth.signOut();
      setUser(null);
      setSession(null);
      setToken(null);
      
      showToast({
        title: "Session Expired",
        message: i18n.t("auth.sessionExpired"),
        variant: "error"
      });
    }
  }, [scheduleRefresh, showToast]);

  // Create API client with token provider (memoized to prevent recreations)
  const api = useMemo(() => createAuthenticatedApi(() => token), [token]);

  // Update language when it changes
  useEffect(() => {
    i18n.changeLanguage(language);
    localStorage.setItem("language", language);
  }, [language]);

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      try {
        console.info("🔐 Initializing authentication state...");
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.warn("⚠️ Session error, clearing invalid session:", error.message);
          await supabase.auth.signOut();
          setSession(null);
          setUser(null);
          setToken(null);
          
          showToast({
            title: "Session Expired",
            message: "Please log in again due to security updates.",
            variant: "error"
          });
        } else {
          console.info("✅ Session retrieved:", session ? "Valid session" : "No active session");
          setSession(session);
          setUser(session?.user ?? null);
          setToken(session?.access_token ?? null);
          scheduleRefresh(session);
        }
      } catch (err) {
        console.error("❌ Error initializing auth:", err);
      } finally {
        setLoading(false);
      }
    };
    
    initAuth();
    
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      console.info("🔐 Auth state changed:", _event);
      setSession(session);
      setUser(session?.user ?? null);
      setToken(session?.access_token ?? null);
      setLoading(false);
      scheduleRefresh(session);
    });

    // Cleanup on unmount
    return () => {
      subscription.unsubscribe();
      if (refreshTimer.current) {
        clearTimeout(refreshTimer.current);
      }
    };
  }, [scheduleRefresh, showToast]);

  /**
   * Log in with email and password
   */
  const login = async (email: string, password: string) => {
    try {
      console.info("🔐 Attempting login for:", email);
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      
      if (error) throw error;
      console.info("✅ Login successful");
    } catch (error) {
      console.error("❌ Login failed:", error);
      throw error;
    }
  };

  /**
   * Register a new user
   */
  const register = async (email: string, password: string) => {
    try {
      console.info("🔐 Attempting registration for:", email);
      const { error } = await supabase.auth.signUp({
        email,
        password,
      });
      
      if (error) throw error;
      console.info("✅ Registration successful");
    } catch (error) {
      console.error("❌ Registration failed:", error);
      throw error;
    }
  };

  /**
   * Log out the current user
   */
  const logout = async () => {
    try {
      console.info("🔐 Logging out...");
      const { error } = await supabase.auth.signOut();
      
      if (error) throw error;
      console.info("✅ Logout successful");
    } catch (error) {
      console.error("❌ Logout failed:", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      session,
      token,
      loading,
      login,
      register,
      logout,
      language,
      setLanguage,
      api
    }}>
      {children}
      {toast && (
        <Toast
          title={toast.title}
          message={toast.message}
          variant={toast.variant}
          onClose={() => setToast(null)}
        />
      )}
    </AuthContext.Provider>
  );
};

/**
 * Hook to access the auth context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
