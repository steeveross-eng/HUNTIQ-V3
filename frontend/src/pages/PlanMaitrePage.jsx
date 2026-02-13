/**
 * PlanMaitrePage - Plan Maître Dashboard wrapper page
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { PlanMaitreDashboard } from '../modules/planmaitre';

const PlanMaitrePage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-planmaitre"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Plan Maître Dashboard */}
        <PlanMaitreDashboard 
          coordinates={{ lat: 46.8139, lng: -71.2082 }}
        />
      </div>
    </main>
  );
};

export default PlanMaitrePage;
