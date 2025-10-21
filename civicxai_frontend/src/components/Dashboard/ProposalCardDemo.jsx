import React, { useState } from 'react';
import ProposalCard from './ProposalCard';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

/**
 * Demo component showing how to use ProposalCard with hooks integration
 */
const ProposalCardDemo = () => {
  const [proposals, setProposals] = useState([
    {
      id: '1',
      title: 'Community Water Infrastructure Project',
      description: 'Proposal to build sustainable water infrastructure in rural communities affected by drought.',
      status: 'in_review',
      type: 'infrastructure',
      date: '2025-10-15',
      metrics: {
        poverty_index: 0.75,
        project_impact: 0.85,
        deforestation: 0.45,
        corruption_risk: 0.25,
      }
    },
    {
      id: '2',
      title: 'Education Technology Initiative',
      description: 'Deploy digital learning platforms to schools in underserved areas.',
      status: 'pending',
      type: 'community',
      date: '2025-10-20',
      metrics: {
        poverty_index: 0.65,
        project_impact: 0.78,
        deforestation: 0.20,
        corruption_risk: 0.30,
      }
    },
    {
      id: '3',
      title: 'Renewable Energy Allocation',
      description: 'Fund solar panel installation in regions with frequent power outages.',
      status: 'approved',
      type: 'allocation',
      date: '2025-10-10',
      metrics: {
        poverty_index: 0.70,
        project_impact: 0.90,
        deforestation: 0.35,
        corruption_risk: 0.15,
      }
    },
    {
      id: '4',
      title: 'Healthcare Access Program',
      description: 'Establish mobile clinics and telemedicine services in remote areas.',
      status: 'in_review',
      type: 'governance',
      date: '2025-10-18',
      metrics: {
        poverty_index: 0.80,
        project_impact: 0.88,
        deforestation: 0.30,
        corruption_risk: 0.20,
      }
    }
  ]);

  const handleViewDetails = (id) => {
    console.log('View details for proposal:', id);
    // Navigate to proposal details page or open modal
  };

  const handleUpdate = (updatedData) => {
    console.log('Proposal updated:', updatedData);
    // Update proposal in state
    if (updatedData.id) {
      setProposals(prev => 
        prev.map(p => p.id === updatedData.id ? { ...p, ...updatedData } : p)
      );
    }
  };

  const refreshProposals = () => {
    console.log('Refreshing proposals...');
    // In real app, fetch from API
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Proposals</h2>
          <p className="text-slate-400 mt-1">
            Review and analyze proposals with AI-powered insights
          </p>
        </div>
        <Button
          onClick={refreshProposals}
          variant="outline"
          className="bg-slate-800 border-slate-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Proposal Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {proposals.map((proposal) => (
          <ProposalCard
            key={proposal.id}
            {...proposal}
            onViewDetails={handleViewDetails}
            onUpdate={handleUpdate}
          />
        ))}
      </div>

      {/* Usage Instructions */}
      <div className="mt-8 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-2">
          🎯 ProposalCard Features
        </h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li>✅ <strong>MeTTa Priority Calculation:</strong> Click "Priority" to calculate using local AI engine</li>
          <li>✅ <strong>Gateway AI Analysis:</strong> Click "AI Analysis" for advanced analysis with uAgents</li>
          <li>✅ <strong>Real-time Metrics:</strong> Displays poverty index, project impact, and more</li>
          <li>✅ <strong>Status Tracking:</strong> Visual status indicators with color coding</li>
          <li>✅ <strong>Interactive:</strong> Click card to view details, buttons for AI actions</li>
        </ul>
      </div>
    </div>
  );
};

export default ProposalCardDemo;
