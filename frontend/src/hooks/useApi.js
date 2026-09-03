import { useState, useCallback } from 'react';
import apiClient from '../api/client';

/**
 * Generic API hook — handles loading, error, and data state.
 * Usage: const { data, loading, error, call } = useApi(apiClient.deviceLongevity);
 */
export function useApi(apiFn) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const call = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFn(payload);
      setData(res.data);
      return res.data;
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Unknown error';
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiFn]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { data, loading, error, call, reset };
}
