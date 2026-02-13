/**
 * CustomerCard - Customer display card
 * Phase 9 - Business Modules
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';

export const CustomerCard = ({ customer, onSelect, compact = false }) => {
  if (!customer) return null;

  const getStatusInfo = (status) => {
    const statuses = {
      new: { label: 'Nouveau', icon: '🆕', color: 'blue' },
      active: { label: 'Actif', icon: '✓', color: 'emerald' },
      inactive: { label: 'Inactif', icon: '⏸️', color: 'slate' },
      vip: { label: 'VIP', icon: '⭐', color: 'amber' }
    };
    return statuses[status] || { label: status, icon: '👤', color: 'slate' };
  };

  const statusInfo = getStatusInfo(customer.status);

  if (compact) {
    return (
      <div 
        className="flex items-center gap-3 bg-slate-800 rounded-lg p-3 border border-slate-700 cursor-pointer hover:border-slate-500"
        onClick={() => onSelect?.(customer)}
      >
        <span className="text-xl">{statusInfo.icon}</span>
        <div className="flex-1">
          <p className="text-white text-sm font-medium">{customer.name || customer.email}</p>
          <p className="text-slate-400 text-xs">{customer.orders_count || 0} commandes</p>
        </div>
        <Badge className={`bg-${statusInfo.color}-900/50 text-${statusInfo.color}-400`}>
          {statusInfo.label}
        </Badge>
      </div>
    );
  }

  return (
    <Card 
      className="bg-slate-800 border-slate-700 cursor-pointer hover:border-slate-500 transition-colors"
      onClick={() => onSelect?.(customer)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-white font-semibold">{customer.name || 'Client'}</h3>
            <p className="text-slate-400 text-sm">{customer.email}</p>
          </div>
          <Badge className={`bg-${statusInfo.color}-900/50 text-${statusInfo.color}-400`}>
            {statusInfo.icon} {statusInfo.label}
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-4">
          <div className="text-center">
            <div className="text-lg font-bold text-blue-400">{customer.orders_count || 0}</div>
            <div className="text-xs text-slate-400">Commandes</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-emerald-400">
              {(customer.total_spent || 0).toFixed(0)}$
            </div>
            <div className="text-xs text-slate-400">Total</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-amber-400">
              {customer.last_order ? new Date(customer.last_order).toLocaleDateString('fr-CA', { month: 'short', day: 'numeric' }) : '-'}
            </div>
            <div className="text-xs text-slate-400">Dernière</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CustomerCard;
