/**
 * TerritoryFilter - Territory type selection and analysis
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Filter, Target, X, Loader2 } from 'lucide-react';

// Territory Types Configuration
export const TERRITORY_TYPES = {
  zec: { name: 'ZEC', color: '#22c55e', icon: '🏕️' },
  sepaq: { name: 'Réserve faunique', color: '#3b82f6', icon: '🦌' },
  clic: { name: 'Zone Clic', color: '#f59e0b', icon: '🟠' },
  pourvoirie: { name: 'Pourvoirie', color: '#8b5cf6', icon: '🟣' },
  prive: { name: 'Territoire privé', color: '#ef4444', icon: '🔴' },
  refuge: { name: 'Refuge faunique', color: '#06b6d4', icon: '🔷' }
};

const TerritoryFilter = ({
  selectedTerritoryType,
  onTerritoryTypeChange,
  selectedZoneNumber,
  onZoneNumberChange,
  onAnalyze,
  onClear,
  loading,
  hasAnalysis
}) => {
  // Get hint text based on territory type
  const getHintText = () => {
    switch (selectedTerritoryType) {
      case 'zec': return 'Ex: 086, 027, 037';
      case 'sepaq': return 'Ex: 13, 08, 04';
      case 'clic': return 'Ex: 27, 10';
      case 'pourvoirie': return 'Ex: domaine-shannon, club-triton';
      default: return '';
    }
  };

  return (
    <Card className="bg-background border-border mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center gap-2">
          <Filter className="h-4 w-4 text-green-500" />
          Filtre Territoire
          <Badge className="ml-auto bg-green-500/20 text-green-400 text-[9px]">FédéCP</Badge>
        </CardTitle>
        <CardDescription className="text-xs">
          Recherchez ZEC, Sépaq, Pourvoiries, Zones Clic...
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <Label className="text-gray-400 text-xs">Type de territoire</Label>
          <Select value={selectedTerritoryType} onValueChange={onTerritoryTypeChange}>
            <SelectTrigger className="bg-card border-border mt-1">
              <SelectValue placeholder="Sélectionnez un type..." />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(TERRITORY_TYPES).map(([key, val]) => (
                <SelectItem key={key} value={key}>
                  {val.icon} {val.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label className="text-gray-400 text-xs">Numéro de zone</Label>
          <Input
            value={selectedZoneNumber}
            onChange={(e) => onZoneNumberChange(e.target.value)}
            placeholder="Ex: 086, 13, domaine-shannon"
            className="bg-card border-border mt-1"
          />
          {selectedTerritoryType && (
            <p className="text-[10px] text-gray-500 mt-1">
              {getHintText()}
            </p>
          )}
        </div>

        <Button
          onClick={onAnalyze}
          disabled={loading || !selectedTerritoryType || !selectedZoneNumber}
          className="w-full bg-green-600 hover:bg-green-700"
          size="sm"
        >
          {loading ? (
            <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Analyse...</>
          ) : (
            <><Target className="h-3 w-3 mr-1" /> Analyser le territoire</>
          )}
        </Button>

        {hasAnalysis && (
          <Button
            variant="outline"
            onClick={onClear}
            className="w-full text-red-400 border-red-400/50"
            size="sm"
          >
            <X className="h-3 w-3 mr-1" /> Effacer analyse
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

export default TerritoryFilter;
