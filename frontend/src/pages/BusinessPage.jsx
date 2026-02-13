/**
 * BusinessPage - Business Dashboard wrapper page
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { BusinessDashboard } from '../modules/business';

const BusinessPage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-business"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Business Dashboard */}
        <BusinessDashboard />
      </div>
    </main>
  );
};

export default BusinessPage;
