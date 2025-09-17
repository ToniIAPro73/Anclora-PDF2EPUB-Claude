import React, { useState, useEffect, useCallback } from 'react';
import Toast from './Toast';
import { ApiClient } from '../lib/apiClient';

interface ConnectionStatusProps {
  checkInterval?: number; // How often to check connection in ms
  maxRetries?: number; // Maximum number of retries
  retryDelay?: number; // Delay between retries in ms
}

/**
 * ConnectionStatus component monitors network connectivity and API availability
 * Displays notifications when connection issues are detected and when connection is restored
 */
const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  checkInterval = 10000, // Check every 10 seconds by default
  maxRetries = 3,
  retryDelay = 2000,
}) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [apiAvailable, setApiAvailable] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastVariant, setToastVariant] = useState<'success' | 'error' | 'warning' | 'info'>('warning');
  
  // Subscribe to ApiClient connection status changes
  useEffect(() => {
    const unsubscribe = ApiClient.addConnectionStatusListener(() => {
      const status = ApiClient.getConnectionStatus();
      setApiAvailable(status.isConnected);
      
      if (!status.isConnected && status.failedAttempts > 0) {
        // Show warning on first failure, error on subsequent failures
        const variant = status.failedAttempts > 2 ? 'error' : 'warning';
        setToastVariant(variant);
        setToastMessage(
          status.failedAttempts > 3
            ? 'No se pudo establecer conexión. Por favor, recarga la página.'
            : 'Problemas de conexión detectados. Intentando reconectar...'
        );
        setShowToast(true);
      } else if (status.isConnected && retryCount > 0) {
        // Show success message when connection is restored
        setToastVariant('success');
        setToastMessage('Conexión restablecida');
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
        setRetryCount(0);
      }
    });
    
    return () => unsubscribe();
  }, [retryCount]);

  // Function to check API availability
  const checkApiConnection = useCallback(async () => {
    if (!navigator.onLine) {
      setApiAvailable(false);
      return;
    }

    // Get current connection status from ApiClient
    const status = ApiClient.getConnectionStatus();
    
    // If ApiClient already knows we're disconnected, don't make another request
    if (!status.isConnected && status.failedAttempts > 3) {
      setApiAvailable(false);
      setRetryCount(prev => prev + 1);
      return;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch('/api/health', {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
        },
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        // Connection is good - ApiClient will be updated by the fetch operation
        if (!apiAvailable) {
          // Connection restored
          setToastMessage('Conexión restablecida');
          setToastVariant('success');
          setShowToast(true);
          setTimeout(() => setShowToast(false), 3000);
        }
        setApiAvailable(true);
        setRetryCount(0);
      } else {
        handleConnectionIssue('API error');
      }
    } catch (error) {
      // Don't count browser offline as a retry
      if (navigator.onLine) {
        handleConnectionIssue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  }, [apiAvailable]);

  // Handle connection issues
  const handleConnectionIssue = (errorMessage: string) => {
    console.warn(`Connection issue detected: ${errorMessage}`);
    
    if (apiAvailable) {
      // First time detecting issue
      setApiAvailable(false);
      setToastMessage('Problemas de conexión detectados. Intentando reconectar...');
      setToastVariant('warning');
      setShowToast(true);
    } else if (retryCount >= maxRetries) {
      // Max retries reached
      setToastMessage('No se pudo establecer conexión. Por favor, recarga la página.');
      setToastVariant('error');
      setShowToast(true);
    }
    
    // Increment retry count
    setRetryCount(prev => prev + 1);
  };

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      checkApiConnection();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setApiAvailable(false);
      setToastMessage('Sin conexión a internet');
      setToastVariant('error');
      setShowToast(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [checkApiConnection]);

  // Periodically check API connection
  useEffect(() => {
    // Initial check
    checkApiConnection();

    // Set up interval for periodic checks
    const intervalId = setInterval(checkApiConnection, checkInterval);

    return () => clearInterval(intervalId);
  }, [checkApiConnection, checkInterval]);

  // Retry logic when connection is lost
  useEffect(() => {
    if (!apiAvailable && isOnline && retryCount < maxRetries) {
      const retryId = setTimeout(() => {
        console.info(`Retry attempt ${retryCount + 1}/${maxRetries}`);
        checkApiConnection();
      }, retryDelay);

      return () => clearTimeout(retryId);
    }
  }, [apiAvailable, isOnline, retryCount, maxRetries, retryDelay, checkApiConnection]);

  return (
    <>
      {showToast && (
        <Toast
          title={isOnline && apiAvailable ? 'Conexión' : 'Problema de conexión'}
          message={toastMessage}
          variant={toastVariant}
          onClose={() => setShowToast(false)}
        />
      )}
    </>
  );
};

export default ConnectionStatus;