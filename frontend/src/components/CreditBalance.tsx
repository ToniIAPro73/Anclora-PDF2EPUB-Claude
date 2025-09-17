import React, { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from 'react-i18next';

interface CreditBalance {
  current_credits: number;
  total_earned: number;
  total_spent: number;
  referral_code?: string;
}

interface CreditBalanceProps {
  onCreditsUpdate?: (credits: number) => void;
  showDetails?: boolean;
  className?: string;
}

const CreditBalance: React.FC<CreditBalanceProps> = ({
  onCreditsUpdate,
  showDetails = false,
  className = ""
}) => {
  const [balance, setBalance] = useState<CreditBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token, api } = useAuth();
  const { t } = useTranslation();

  const fetchBalance = async () => {
    try {
      setLoading(true);

      // Verificar que el API client existe
      if (!api) {
        console.warn('🔐 No API client available for credit balance request');
        setError('Authentication required');
        setLoading(false);
        return;
      }

      const response = await api.get<{success: boolean, balance: CreditBalance}>('credits/balance');

      if (response.success && response.balance) {
        setBalance(response.balance);
        onCreditsUpdate?.(response.balance.current_credits);
      } else {
        setError('No se pudo obtener el balance de créditos');
      }
    } catch (err) {
      console.error('Error fetching credit balance:', err);
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (api && token) {
      fetchBalance();
    } else if (token === null) {
      // Token is explicitly null, user is not authenticated
      setError('Authentication required');
      setLoading(false);
    }
  }, [api, token]);

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        <span className="text-sm text-gray-500">{t('credits.loading')}</span>
      </div>
    );
  }

  if (error || !balance) {
    return (
      <div className={`flex items-center space-x-2 text-red-500 ${className}`}>
        <span className="text-sm">⚠️ {error || t('credits.error')}</span>
        <span
          onClick={fetchBalance}
          className="text-xs underline hover:no-underline cursor-pointer"
        >
          {t('credits.retry')}
        </span>
      </div>
    );
  }

  const getCreditColor = (credits: number) => {
    if (credits <= 10) return 'text-red-600';
    if (credits <= 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getCreditIcon = (credits: number) => {
    if (credits <= 10) return '🪙';
    if (credits <= 50) return '💰';
    return '✨';
  };

  return (
    <div className={`credit-balance ${className}`}>
      {/* Vista compacta */}
      <div className="flex items-center space-x-2">
        <span className="text-lg">{getCreditIcon(balance.current_credits)}</span>
        <div className="flex flex-col">
          <span className={`font-bold text-lg ${getCreditColor(balance.current_credits)}`}>
            {balance.current_credits.toLocaleString()}
          </span>
          <span className="text-xs text-gray-500">{t('credits.available')}</span>
        </div>
      </div>

      {/* Vista detallada */}
      {showDetails && (
        <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
          <h4 className="font-semibold text-sm text-gray-700 mb-2">
            {t('credits.summary')}
          </h4>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">{t('credits.earned')}:</span>
              <span className="font-medium text-green-600 ml-1">
                +{balance.total_earned.toLocaleString()}
              </span>
            </div>

            <div>
              <span className="text-gray-500">{t('credits.spent')}:</span>
              <span className="font-medium text-red-600 ml-1">
                -{balance.total_spent.toLocaleString()}
              </span>
            </div>
          </div>

          {balance.referral_code && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <span className="text-xs text-gray-500">{t('credits.referralCode')}:</span>
              <code className="ml-1 px-1 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                {balance.referral_code}
              </code>
            </div>
          )}

          {balance.current_credits <= 10 && (
            <div className="mt-2 p-2 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <p className="text-xs text-yellow-800">
                ⚠️ {t('credits.lowBalance')}
              </p>
              <button className="text-xs text-blue-600 underline hover:no-underline mt-1">
                {t('credits.getMore')}
              </button>
            </div>
          )}

          <button
            onClick={fetchBalance}
            className="mt-2 text-xs text-blue-600 underline hover:no-underline"
          >
            🔄 {t('credits.refresh')}
          </button>
        </div>
      )}
    </div>
  );
};

export default CreditBalance;