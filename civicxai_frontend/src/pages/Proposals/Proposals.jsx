import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ProposalCard from '@/components/Dashboard/ProposalCard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Search, 
  Filter, 
  Plus,
  LayoutGrid,
  List,
  SlidersHorizontal
} from 'lucide-react';
import { allocationRequestsAPI } from '@/services/api';
import { toast } from 'sonner';

const Proposals = () => {
  const navigate = useNavigate();
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    setLoading(true);
    try {
      const response = await allocationRequestsAPI.list();
      if (response.data?.success) {
        setProposals(response.data.data || []);
      }
    } catch (error) {
      console.error('Failed to load proposals:', error);
      // Generate mock data for demonstration
      generateMockProposals();
    } finally {
      setLoading(false);
    }
  };

  const generateMockProposals = () => {
    const mockData = [
      {
        id: 1,
        title: 'North Region Infrastructure',
        status: 'pending',
        type: 'infrastructure',
        date: '2 days ago',
        description: 'Budget allocation for road and bridge development in northern provinces',
        region_name: 'North Region',
        metrics: {
          poverty_index: 0.85,
          project_impact: 0.90,
          environmental_score: 0.75,
          corruption_risk: 0.30
        }
      },
      {
        id: 2,
        title: 'Education Initiative - South',
        status: 'in_review',
        type: 'community',
        date: '5 days ago',
        description: 'Schools and teacher training program funding request',
        region_name: 'South Region',
        metrics: {
          poverty_index: 0.72,
          project_impact: 0.85,
          environmental_score: 0.40,
          corruption_risk: 0.25
        }
      },
      {
        id: 3,
        title: 'Healthcare Expansion - Central',
        status: 'approved',
        type: 'allocation',
        date: '1 week ago',
        description: 'Hospital construction and medical equipment procurement',
        region_name: 'Central Region',
        metrics: {
          poverty_index: 0.65,
          project_impact: 0.92,
          environmental_score: 0.35,
          corruption_risk: 0.20
        }
      },
      {
        id: 4,
        title: 'Environmental Conservation',
        status: 'pending',
        type: 'governance',
        date: '3 days ago',
        description: 'Forest preservation and wildlife protection program',
        region_name: 'East Region',
        metrics: {
          poverty_index: 0.55,
          project_impact: 0.78,
          environmental_score: 0.88,
          corruption_risk: 0.28
        }
      },
      {
        id: 5,
        title: 'Water Infrastructure Project',
        status: 'in_review',
        type: 'infrastructure',
        date: '4 days ago',
        description: 'Clean water access and sanitation facilities',
        region_name: 'West Region',
        metrics: {
          poverty_index: 0.78,
          project_impact: 0.88,
          environmental_score: 0.65,
          corruption_risk: 0.35
        }
      },
      {
        id: 6,
        title: 'Agricultural Development',
        status: 'pending',
        type: 'community',
        date: '6 days ago',
        description: 'Farm equipment and irrigation system upgrades',
        region_name: 'Rural Areas',
        metrics: {
          poverty_index: 0.80,
          project_impact: 0.75,
          environmental_score: 0.55,
          corruption_risk: 0.40
        }
      }
    ];
    setProposals(mockData);
  };

  const filteredProposals = proposals.filter(proposal => {
    const matchesSearch = proposal.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proposal.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proposal.region_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (activeTab === 'all') return matchesSearch;
    return matchesSearch && proposal.status?.toLowerCase() === activeTab;
  });

  const getStatusCount = (status) => {
    if (status === 'all') return proposals.length;
    return proposals.filter(p => p.status?.toLowerCase() === status).length;
  };

  return (
    <div className="p-4 lg:p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Proposals</h1>
            <p className="text-slate-400">Browse and interact with governance proposals</p>
          </div>
          <Button 
            onClick={() => navigate('/ai-gateway')}
            className="bg-violet-600 hover:bg-violet-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Proposal
          </Button>
        </div>

        {/* Search and Filter Bar */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-4">
            <div className="flex flex-col lg:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search proposals by title, description, or region..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-slate-900 border-slate-700 text-white"
                />
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="icon"
                  className="bg-slate-900 border-slate-700 hover:bg-slate-800"
                >
                  <SlidersHorizontal className="w-4 h-4" />
                </Button>
                <div className="flex rounded-md border border-slate-700 bg-slate-900">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setViewMode('grid')}
                    className={viewMode === 'grid' ? 'bg-violet-600/20 text-violet-400' : 'text-slate-400'}
                  >
                    <LayoutGrid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setViewMode('list')}
                    className={viewMode === 'list' ? 'bg-violet-600/20 text-violet-400' : 'text-slate-400'}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tabs for Status Filter */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList className="bg-slate-800 border-slate-700">
          <TabsTrigger value="all" className="data-[state=active]:bg-violet-600">
            All ({getStatusCount('all')})
          </TabsTrigger>
          <TabsTrigger value="pending" className="data-[state=active]:bg-violet-600">
            Pending ({getStatusCount('pending')})
          </TabsTrigger>
          <TabsTrigger value="in_review" className="data-[state=active]:bg-violet-600">
            In Review ({getStatusCount('in_review')})
          </TabsTrigger>
          <TabsTrigger value="approved" className="data-[state=active]:bg-violet-600">
            Approved ({getStatusCount('approved')})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Proposals Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-violet-500"></div>
          <p className="text-slate-400 mt-4">Loading proposals...</p>
        </div>
      ) : filteredProposals.length === 0 ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="py-12 text-center">
            <p className="text-slate-400">No proposals found</p>
            {searchTerm && (
              <Button 
                variant="link" 
                onClick={() => setSearchTerm('')}
                className="text-violet-400 mt-2"
              >
                Clear search
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
              : 'space-y-4'
          }
        >
          {filteredProposals.map((proposal, index) => (
            <motion.div
              key={proposal.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <ProposalCard
                id={proposal.id}
                title={proposal.title}
                status={proposal.status}
                type={proposal.type}
                date={proposal.date}
                description={proposal.description}
                metrics={proposal.metrics}
                onUpdate={loadProposals}
              />
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
};

export default Proposals;
