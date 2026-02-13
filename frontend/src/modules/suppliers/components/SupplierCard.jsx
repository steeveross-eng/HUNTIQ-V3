/**
 * SupplierCard - Supplier display card
 * Phase 9 - Business Modules
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';

export const SupplierCard = ({ supplier, onSelect, compact = false }) => {
  if (!supplier) return null;

  const getTypeInfo = (type) => {
    const types = {
      manufacturer: { label: 'Fabricant', icon: '🏭', color: 'blue' },
      distributor: { label: 'Distributeur', icon: '🚚', color: 'purple' },
      retailer: { label: 'Détaillant', icon: '🏪', color: 'emerald' },
      dropshipper: { label: 'Dropshipper', icon: '📦', color: 'amber' }
    };
    return types[type] || { label: type, icon: '🏢', color: 'slate' };
  };

  const typeInfo = getTypeInfo(supplier.type);

  if (compact) {
    return (
      <div 
        className="flex items-center gap-3 bg-slate-800 rounded-lg p-3 border border-slate-700 cursor-pointer hover:border-slate-500"
        onClick={() => onSelect?.(supplier)}
      >
        <span className="text-xl">{typeInfo.icon}</span>
        <div className="flex-1">
          <p className="text-white text-sm font-medium">{supplier.name}</p>
          <p className="text-slate-400 text-xs">{typeInfo.label}</p>
        </div>
        <Badge className={`${supplier.is_active ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}>
          {supplier.is_active ? 'Actif' : 'Inactif'}
        </Badge>
      </div>
    );
  }

  return (
    <Card 
      className="bg-slate-800 border-slate-700 cursor-pointer hover:border-slate-500 transition-colors"
      onClick={() => onSelect?.(supplier)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{typeInfo.icon}</span>
            <div>
              <h3 className="text-white font-semibold">{supplier.name}</h3>
              <Badge className={`bg-${typeInfo.color}-900/50 text-${typeInfo.color}-400 text-xs`}>
                {typeInfo.label}
              </Badge>
            </div>
          </div>
          <Badge className={`${supplier.is_active ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}>
            {supplier.is_active ? '● Actif' : '○ Inactif'}
          </Badge>
        </div>

        {supplier.contact_email && (
          <p className="text-slate-400 text-sm mb-2">
            📧 {supplier.contact_email}
          </p>
        )}

        {supplier.products_count !== undefined && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-slate-300">
              📦 {supplier.products_count} produits
            </span>
            {supplier.commission_rate && (
              <span className="text-amber-400">
                💰 {supplier.commission_rate}% commission
              </span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SupplierCard;
