/**
 * BIONIC™ P3 - BehaviorV3Panel Component
 * =======================================
 * Panneau de visualisation minimaliste pour le CalibrationHistoryTracker.
 * 
 * Fonctionnalités:
 * - Affichage du statut du moteur
 * - Visualisation des pondérations actuelles
 * - Historique des calibrations
 * - Actions: Train, Calibrate, Rollback
 */

import React, { useState } from 'react';
import { 
  useBehaviorV3Status, 
  useBehaviorV3Weights, 
  useBehaviorV3Training,
  useBehaviorV3Calibration,
  useBehaviorV3History,
  useBehaviorV3Metrics
} from '../../hooks/useBehaviorV3';

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

const StatusBadge = ({ status }) => {
  const colors = {
    operational: 'bg-green-500',
    maintenance: 'bg-yellow-500',
    error: 'bg-red-500',
  };
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs text-white ${colors[status] || 'bg-gray-500'}`}>
      {status === 'operational' ? 'Opérationnel' : status === 'maintenance' ? 'Maintenance' : status}
    </span>
  );
};

const WeightBar = ({ label, value, color = 'bg-amber-500' }) => {
  const percentage = Math.round(value * 100);
  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm text-gray-300 mb-1">
        <span>{label}</span>
        <span>{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

const CalibrationCard = ({ record, isActive }) => {
  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-CA', { 
      day: '2-digit', 
      month: 'short', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  return (
    <div className={`p-3 rounded-lg border ${isActive ? 'border-amber-500 bg-amber-500/10' : 'border-gray-700 bg-gray-800/50'}`}>
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="text-sm font-medium text-white">{record.species}</span>
          <span className="text-xs text-gray-400 ml-2">{record.territory}</span>
        </div>
        {isActive && (
          <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded">
            Active
          </span>
        )}
      </div>
      <div className="text-xs text-gray-400">
        <div>📅 {formatDate(record.timestamp)}</div>
        <div>📈 +{record.improvement_score}% amélioration</div>
        <div>🎯 {Math.round(record.confidence * 100)}% confiance</div>
      </div>
    </div>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const BehaviorV3Panel = ({ className = '' }) => {
  const [activeTab, setActiveTab] = useState('status');
  const [trainingOptions, setTrainingOptions] = useState({
    species: 'deer',
    maxIterations: 100,
  });
  
  // Hooks
  const { status, loading: statusLoading, refetch: refetchStatus } = useBehaviorV3Status();
  const { weights, loading: weightsLoading, refetch: refetchWeights } = useBehaviorV3Weights();
  const { train, training, loading: trainingLoading } = useBehaviorV3Training();
  const { calibrate, calibration, loading: calibrationLoading } = useBehaviorV3Calibration();
  const { history, loading: historyLoading, refetch: refetchHistory } = useBehaviorV3History();
  const { metrics, loading: metricsLoading } = useBehaviorV3Metrics();
  
  // Handlers
  const handleTrain = async () => {
    try {
      await train({
        useSimulatedData: true,
        useFeedbackData: true,
        speciesFilter: [trainingOptions.species],
        maxIterations: trainingOptions.maxIterations,
      });
      refetchWeights();
    } catch (e) {
      console.error('Training error:', e);
    }
  };
  
  const handleCalibrate = async () => {
    try {
      await calibrate({
        species: trainingOptions.species,
        territory: 'quebec',
      });
      refetchWeights();
      refetchHistory();
    } catch (e) {
      console.error('Calibration error:', e);
    }
  };
  
  // Loading state
  if (statusLoading && !status) {
    return (
      <div className={`bg-gray-900/90 border border-gray-800 rounded-xl p-6 ${className}`}>
        <div className="flex items-center justify-center h-40">
          <div className="animate-spin h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className={`bg-gray-900/90 border border-gray-800 rounded-xl overflow-hidden ${className}`}
      data-testid="behavior-v3-panel"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
            <span className="text-xl">🧠</span>
          </div>
          <div>
            <h3 className="text-white font-semibold">
              BehaviorEngine v3.0
            </h3>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>P3 Auto-Calibrant</span>
              <StatusBadge status={status?.status || 'unknown'} />
            </div>
          </div>
        </div>
        
        <button
          onClick={() => {
            refetchStatus();
            refetchWeights();
            refetchHistory();
          }}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          title="Rafraîchir"
        >
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      {/* Tabs */}
      <div className="flex border-b border-gray-800">
        {['status', 'weights', 'history', 'actions'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab 
                ? 'text-amber-400 border-b-2 border-amber-400' 
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            {tab === 'status' && '📊 Statut'}
            {tab === 'weights' && '⚖️ Poids'}
            {tab === 'history' && '📜 Historique'}
            {tab === 'actions' && '⚡ Actions'}
          </button>
        ))}
      </div>
      
      {/* Content */}
      <div className="p-4 max-h-96 overflow-y-auto">
        
        {/* Status Tab */}
        {activeTab === 'status' && status && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <div className="text-xs text-gray-400">Calibrations</div>
                <div className="text-xl font-bold text-white">{status.total_calibrations || 0}</div>
              </div>
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <div className="text-xs text-gray-400">Feedbacks</div>
                <div className="text-xl font-bold text-white">{status.total_feedbacks || 0}</div>
              </div>
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <div className="text-xs text-gray-400">Rollbacks</div>
                <div className="text-xl font-bold text-white">{status.total_rollbacks || 0}</div>
              </div>
              <div className="p-3 bg-gray-800/50 rounded-lg">
                <div className="text-xs text-gray-400">Calibré</div>
                <div className="text-xl font-bold text-white">{status.is_calibrated ? '✅' : '❌'}</div>
              </div>
            </div>
            
            {/* Capabilities */}
            <div className="p-3 bg-gray-800/30 rounded-lg">
              <div className="text-sm font-medium text-gray-300 mb-2">Capacités</div>
              <div className="flex flex-wrap gap-2">
                {status.capabilities && Object.entries(status.capabilities).map(([key, enabled]) => (
                  <span 
                    key={key}
                    className={`px-2 py-1 text-xs rounded ${enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-500'}`}
                  >
                    {key.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Weights Tab */}
        {activeTab === 'weights' && (
          <div className="space-y-4">
            {weightsLoading ? (
              <div className="text-center text-gray-400 py-8">Chargement...</div>
            ) : weights?.current_weights ? (
              <>
                <div className="text-xs text-gray-400 mb-4">
                  {weights.is_default ? '⚠️ Poids par défaut' : '✅ Poids optimisés'}
                  {weights.calibration_id && (
                    <span className="ml-2">ID: {weights.calibration_id}</span>
                  )}
                </div>
                
                <WeightBar label="🏃 Activité" value={weights.current_weights.activity} color="bg-blue-500" />
                <WeightBar label="🍂 Saisonnier" value={weights.current_weights.seasonal} color="bg-amber-500" />
                <WeightBar label="🦌 Mouvement" value={weights.current_weights.movement} color="bg-green-500" />
                <WeightBar label="🌡️ Environnement" value={weights.current_weights.environmental} color="bg-purple-500" />
                <WeightBar label="⏰ Temporel" value={weights.current_weights.temporal} color="bg-pink-500" />
                <WeightBar label="👥 Pression" value={weights.current_weights.pressure} color="bg-red-500" />
              </>
            ) : (
              <div className="text-center text-gray-400 py-8">Aucun poids disponible</div>
            )}
          </div>
        )}
        
        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-3">
            {historyLoading ? (
              <div className="text-center text-gray-400 py-8">Chargement...</div>
            ) : history?.records?.length > 0 ? (
              <>
                <div className="text-xs text-gray-400 mb-2">
                  {history.total_calibrations} calibrations | Taux: {Math.round(history.success_rate)}%
                </div>
                {history.records.slice(0, 5).map((record) => (
                  <CalibrationCard 
                    key={record.id} 
                    record={record} 
                    isActive={record.id === history.active_calibration_id}
                  />
                ))}
              </>
            ) : (
              <div className="text-center text-gray-400 py-8">
                Aucun historique disponible
              </div>
            )}
          </div>
        )}
        
        {/* Actions Tab */}
        {activeTab === 'actions' && (
          <div className="space-y-4">
            {/* Species Selection */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Espèce cible</label>
              <select
                value={trainingOptions.species}
                onChange={(e) => setTrainingOptions(prev => ({ ...prev, species: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:border-amber-500 outline-none"
              >
                <option value="deer">🦌 Cerf</option>
                <option value="moose">🫎 Orignal</option>
                <option value="bear">🐻 Ours</option>
              </select>
            </div>
            
            {/* Actions Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleTrain}
                disabled={trainingLoading}
                className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg font-medium text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {trainingLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Training...
                  </span>
                ) : (
                  '🎯 Entraîner ML'
                )}
              </button>
              
              <button
                onClick={handleCalibrate}
                disabled={calibrationLoading}
                className="px-4 py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-lg font-medium text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {calibrationLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Calibration...
                  </span>
                ) : (
                  '⚡ Calibrer'
                )}
              </button>
            </div>
            
            {/* Results */}
            {training && (
              <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div className="text-sm font-medium text-blue-400 mb-1">Entraînement terminé</div>
                <div className="text-xs text-gray-400">
                  {training.message}
                </div>
              </div>
            )}
            
            {calibration && (
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                <div className="text-sm font-medium text-amber-400 mb-1">Calibration terminée</div>
                <div className="text-xs text-gray-400">
                  +{calibration.improvement_score}% amélioration | {Math.round(calibration.confidence * 100)}% confiance
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-800 bg-gray-800/30">
        <div className="text-xs text-gray-500 text-center">
          BIONIC™ BehaviorEngine v3.0.0 (P3) | Gradient Boosting ML
        </div>
      </div>
    </div>
  );
};

export default BehaviorV3Panel;
