/**
 * UserActivity - User activity feed component
 * Phase 9 - Business Modules
 */
import React from 'react';

export const UserActivity = ({ activities = [], limit = 10 }) => {
  const displayActivities = activities.slice(0, limit);

  const getActivityIcon = (type) => {
    const icons = {
      login: '🔐',
      logout: '🚪',
      purchase: '🛒',
      analyze: '🔬',
      compare: '⚖️',
      favorite: '❤️',
      review: '⭐',
      territory: '🗺️',
      profile_update: '✏️',
      settings: '⚙️'
    };
    return icons[type] || '📋';
  };

  const getActivityColor = (type) => {
    const colors = {
      login: '#10b981',
      logout: '#64748b',
      purchase: '#f59e0b',
      analyze: '#3b82f6',
      compare: '#8b5cf6',
      favorite: '#ef4444',
      review: '#fbbf24',
      territory: '#22c55e'
    };
    return colors[type] || '#64748b';
  };

  if (!displayActivities.length) {
    return (
      <div className="bg-slate-800/50 rounded-lg p-4 text-center">
        <span className="text-3xl">📋</span>
        <p className="text-slate-400 text-sm mt-2">Aucune activité récente</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700">
      <div className="p-3 border-b border-slate-700">
        <h3 className="text-white font-medium flex items-center gap-2">
          <span>📋</span>
          Activité Récente
        </h3>
      </div>
      
      <div className="divide-y divide-slate-700">
        {displayActivities.map((activity, index) => (
          <div key={activity.id || index} className="p-3 hover:bg-slate-700/30 transition-colors">
            <div className="flex items-start gap-3">
              <span 
                className="text-xl flex-shrink-0"
                style={{ filter: `drop-shadow(0 0 4px ${getActivityColor(activity.type)})` }}
              >
                {getActivityIcon(activity.type)}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">
                  {activity.description || activity.type}
                </p>
                <p className="text-slate-400 text-xs">
                  {activity.timestamp 
                    ? new Date(activity.timestamp).toLocaleString('fr-CA')
                    : 'Date inconnue'
                  }
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {activities.length > limit && (
        <div className="p-3 border-t border-slate-700 text-center">
          <button className="text-sm text-blue-400 hover:text-blue-300">
            Voir plus ({activities.length - limit} autres)
          </button>
        </div>
      )}
    </div>
  );
};

export default UserActivity;
