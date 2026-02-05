/**
 * BIONIC™ P3 - useBehaviorV3 Hook
 * =================================
 * Hook React pour consommer les pondérations et fonctionnalités du BehaviorEngine v3.0.
 * 
 * Hooks disponibles:
 * - useBehaviorV3Status: Statut du moteur
 * - useBehaviorV3Weights: Pondérations actuelles
 * - useBehaviorV3Training: Entraînement ML
 * - useBehaviorV3Calibration: Calibration
 * - useBehaviorV3History: Historique des calibrations
 * - useBehaviorV3Feedback: Soumission de feedback
 */

import { useState, useCallback, useEffect } from 'react';
import behaviorV3Service from '../services/behaviorV3.service';

/**
 * Hook principal pour le statut du moteur
 */
export function useBehaviorV3Status() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.getEngineStatus();
      setStatus(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
}

/**
 * Hook pour les pondérations actuelles
 */
export function useBehaviorV3Weights() {
  const [weights, setWeights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWeights = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.getCurrentWeights();
      setWeights(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWeights();
  }, [fetchWeights]);

  return { weights, loading, error, refetch: fetchWeights };
}

/**
 * Hook pour l'entraînement ML
 */
export function useBehaviorV3Training() {
  const [training, setTraining] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const train = useCallback(async (options = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.trainModel(options);
      setTraining(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { training, loading, error, train };
}

/**
 * Hook pour la calibration
 */
export function useBehaviorV3Calibration() {
  const [calibration, setCalibration] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calibrate = useCallback(async (options = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.calibrateWeights(options);
      setCalibration(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { calibration, loading, error, calibrate };
}

/**
 * Hook pour l'historique des calibrations
 */
export function useBehaviorV3History(options = {}) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async (fetchOptions = options) => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.getCalibrationHistory(fetchOptions);
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, []);

  return { history, loading, error, refetch: fetchHistory };
}

/**
 * Hook pour les métriques
 */
export function useBehaviorV3Metrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.getEngineMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, loading, error, refetch: fetchMetrics };
}

/**
 * Hook pour la soumission de feedback
 */
export function useBehaviorV3Feedback() {
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submitFeedback = useCallback(async (feedbackData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.submitFeedback(feedbackData);
      setFeedback(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { feedback, loading, error, submitFeedback };
}

/**
 * Hook pour le rollback
 */
export function useBehaviorV3Rollback() {
  const [rollbackResult, setRollbackResult] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCandidates = useCallback(async (limit = 10) => {
    try {
      const data = await behaviorV3Service.getRollbackCandidates(limit);
      setCandidates(data.candidates || []);
      return data;
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const rollback = useCallback(async (calibrationId, reason, notes = null) => {
    setLoading(true);
    setError(null);
    try {
      const data = await behaviorV3Service.rollbackCalibration(calibrationId, reason, notes);
      setRollbackResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { rollbackResult, candidates, loading, error, fetchCandidates, rollback };
}

/**
 * Hook combiné pour toutes les fonctionnalités
 */
export function useBehaviorV3() {
  const statusHook = useBehaviorV3Status();
  const weightsHook = useBehaviorV3Weights();
  const trainingHook = useBehaviorV3Training();
  const calibrationHook = useBehaviorV3Calibration();
  const historyHook = useBehaviorV3History();
  const metricsHook = useBehaviorV3Metrics();
  const feedbackHook = useBehaviorV3Feedback();
  const rollbackHook = useBehaviorV3Rollback();

  return {
    // Status
    status: statusHook.status,
    statusLoading: statusHook.loading,
    refetchStatus: statusHook.refetch,
    
    // Weights
    weights: weightsHook.weights,
    weightsLoading: weightsHook.loading,
    refetchWeights: weightsHook.refetch,
    
    // Training
    train: trainingHook.train,
    trainingResult: trainingHook.training,
    trainingLoading: trainingHook.loading,
    
    // Calibration
    calibrate: calibrationHook.calibrate,
    calibrationResult: calibrationHook.calibration,
    calibrationLoading: calibrationHook.loading,
    
    // History
    history: historyHook.history,
    historyLoading: historyHook.loading,
    refetchHistory: historyHook.refetch,
    
    // Metrics
    metrics: metricsHook.metrics,
    metricsLoading: metricsHook.loading,
    
    // Feedback
    submitFeedback: feedbackHook.submitFeedback,
    feedbackResult: feedbackHook.feedback,
    feedbackLoading: feedbackHook.loading,
    
    // Rollback
    rollback: rollbackHook.rollback,
    rollbackCandidates: rollbackHook.candidates,
    fetchRollbackCandidates: rollbackHook.fetchCandidates,
    
    // Global error (last error from any hook)
    error: statusHook.error || weightsHook.error || trainingHook.error || 
           calibrationHook.error || historyHook.error || metricsHook.error ||
           feedbackHook.error || rollbackHook.error,
  };
}

export default useBehaviorV3;
