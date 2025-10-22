import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain,
  RefreshCw,
  Search,
  Info,
  Loader2,
  Target,
  FileText,
  TrendingUp
} from 'lucide-react';
import { allocationRequestsAPI, explanationRequestsAPI } from '@/services/api';
import { toast } from 'sonner';
import AllocationRequestCard from './AllocationRequestCard';
import ExplanationRequestCard from './ExplanationRequestCard';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Unified section showing both allocation and explanation requests
 * Integrates AI Gateway with Dashboard - all requests in one place
 */
const AIRequestsSection = () => {
  const [allocationRequests, setAllocationRequests] = useState([]);
  const [explanationRequests, setExplanationRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allocationStats, setAllocationStats] = useState(null);
  const [explanationStats, setExplanationStats] = useState(null);
  const [requestType, setRequestType] = useState('all'); // all, allocations, explanations
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchAllRequests();
  }, []);

  const fetchAllRequests = async () => {
    setLoading(true);
    try {
      // Fetch both types in parallel
      const [allocResponse, explainResponse, allocStatsRes, explainStatsRes] = await Promise.all([
        allocationRequestsAPI.list(),
        explanationRequestsAPI.list(),
        allocationRequestsAPI.stats(),
        explanationRequestsAPI.stats()
      ]);

      setAllocationRequests(allocResponse.data.results || []);
      setExplanationRequests(explainResponse.data.results || []);
      setAllocationStats(allocStatsRes.data.stats);
      setExplanationStats(explainStatsRes.data.stats);
    } catch (error) {
      console.error('Failed to fetch requests:', error);
      toast.error('Failed to load AI requests');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchAllRequests();
    toast.success('Refreshed AI requests');
  };

  const handleViewDetails = (request) => {
    console.log('View details:', request);
    // Could open modal or navigate to details page
  };

  // Combine and filter requests
  const getCombinedRequests = () => {
    let combined = [];

    if (requestType === 'all' || requestType === 'allocations') {
      combined = [
        ...combined,
        ...allocationRequests.map(req => ({ ...req, type: 'allocation' }))
      ];
    }

    if (requestType === 'all' || requestType === 'explanations') {
      combined = [
        ...combined,
        ...explanationRequests.map(req => ({ ...req, type: 'explanation' }))
      ];
    }

    // Filter by status
    if (statusFilter !== 'all') {
      combined = combined.filter(req => req.status === statusFilter);
    }

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      combined = combined.filter(req =>
        req.region_name?.toLowerCase().includes(query) ||
        req.region_id?.toLowerCase().includes(query) ||
        req.context?.toLowerCase().includes(query) ||
        req.notes?.toLowerCase().includes(query)
      );
    }

    // Sort by date (newest first)
    combined.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    return combined;
  };

  const combinedRequests = getCombinedRequests();
  const totalRequests = (allocationStats?.total || 0) + (explanationStats?.total || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-2">
            <Brain className="h-8 w-8 text-violet-500" />
            AI Gateway Requests
          </h2>
          <p className="text-slate-400 mt-1">
            All allocation and explanation requests from AI Gateway
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overview Stats */}
      {allocationStats && explanationStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gradient-to-br from-violet-900/20 to-violet-800/20 border-violet-700/50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Total Requests</p>
                  <p className="text-4xl font-bold text-white">{totalRequests}</p>
                </div>
                <Brain className="h-10 w-10 text-violet-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/20 to-blue-800/20 border-blue-700/50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Allocations</p>
                  <p className="text-4xl font-bold text-blue-400">{allocationStats.total}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {allocationStats.analyzed} analyzed
                  </p>
                </div>
                <Target className="h-10 w-10 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-900/20 to-indigo-800/20 border-indigo-700/50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Explanations</p>
                  <p className="text-4xl font-bold text-indigo-400">{explanationStats.total}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {explanationStats.completed} completed
                  </p>
                </div>
                <FileText className="h-10 w-10 text-indigo-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-900/20 to-green-800/20 border-green-700/50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Completion Rate</p>
                  <p className="text-4xl font-bold text-green-400">
                    {totalRequests > 0 
                      ? Math.round(((allocationStats.analyzed + explanationStats.completed) / totalRequests) * 100)
                      : 0}%
                  </p>
                </div>
                <TrendingUp className="h-10 w-10 text-green-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search by region name, ID, or context..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>

            {/* Request Type Filter */}
            <Tabs value={requestType} onValueChange={setRequestType} className="w-full lg:w-auto">
              <TabsList className="bg-slate-800">
                <TabsTrigger value="all">All Requests</TabsTrigger>
                <TabsTrigger value="allocations">Allocations</TabsTrigger>
                <TabsTrigger value="explanations">Explanations</TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Status Filter */}
            <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-full lg:w-auto">
              <TabsList className="bg-slate-800">
                <TabsTrigger value="all">All Status</TabsTrigger>
                <TabsTrigger value="pending">Pending</TabsTrigger>
                <TabsTrigger value="processing">Processing</TabsTrigger>
                <TabsTrigger value="analyzed">Analyzed</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Requests Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-violet-500" />
        </div>
      ) : combinedRequests.length === 0 ? (
        <Alert className="bg-slate-900 border-slate-800">
          <Info className="h-4 w-4 text-blue-400" />
          <AlertDescription className="text-slate-300">
            {searchQuery 
              ? 'No requests match your search criteria.' 
              : 'No AI requests found. Submit allocation or explanation requests from the AI Gateway!'}
          </AlertDescription>
        </Alert>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <AnimatePresence>
              {combinedRequests.map((request, index) => (
                <motion.div
                  key={`${request.type}-${request.id}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  {request.type === 'allocation' ? (
                    <AllocationRequestCard
                      request={request}
                      onViewDetails={handleViewDetails}
                    />
                  ) : (
                    <ExplanationRequestCard
                      request={request}
                      onViewDetails={handleViewDetails}
                    />
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Show count */}
          <div className="text-center text-slate-500 text-sm">
            Showing {combinedRequests.length} request{combinedRequests.length !== 1 ? 's' : ''}
            {statusFilter !== 'all' && ` (${statusFilter})`}
            {requestType !== 'all' && ` (${requestType})`}
          </div>
        </>
      )}
    </div>
  );
};

export default AIRequestsSection;
