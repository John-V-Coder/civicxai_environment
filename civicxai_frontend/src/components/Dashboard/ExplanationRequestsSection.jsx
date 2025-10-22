import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  FileText,
  RefreshCw,
  Search,
  Clock,
  CheckCircle2,
  Loader2,
  Info,
  Activity,
  Sparkles
} from 'lucide-react';
import { explanationRequestsAPI } from '@/services/api';
import { toast } from 'sonner';
import ExplanationRequestCard from './ExplanationRequestCard';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Dashboard section for viewing all explanation requests
 */
const ExplanationRequestsSection = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);

  useEffect(() => {
    fetchRequests();
    fetchStats();
  }, [statusFilter]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const response = await explanationRequestsAPI.list(params);
      setRequests(response.data.results || []);
    } catch (error) {
      console.error('Failed to fetch explanation requests:', error);
      toast.error('Failed to load explanation requests');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await explanationRequestsAPI.stats();
      setStats(response.data.stats);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleRefresh = () => {
    fetchRequests();
    fetchStats();
    toast.success('Refreshed explanation requests');
  };

  const handleViewDetails = (request) => {
    setSelectedRequest(request);
    console.log('View details:', request);
  };

  // Filter requests by search query
  const filteredRequests = requests.filter(req => 
    req.region_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    req.region_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    req.context?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-2">
            <FileText className="h-8 w-8 text-blue-500" />
            AI Explanation Requests
          </h2>
          <p className="text-slate-400 mt-1">
            Explanations generated through AI Gateway
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Total</p>
                  <p className="text-3xl font-bold text-white">{stats.total}</p>
                </div>
                <Sparkles className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Pending</p>
                  <p className="text-3xl font-bold text-yellow-500">{stats.pending}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Processing</p>
                  <p className="text-3xl font-bold text-blue-500">{stats.processing}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Completed</p>
                  <p className="text-3xl font-bold text-green-500">{stats.completed}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Approved</p>
                  <p className="text-3xl font-bold text-emerald-500">{stats.approved}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-emerald-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search by region, context, or ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>

            {/* Status Filter */}
            <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-full md:w-auto">
              <TabsList className="bg-slate-800">
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="pending">Pending</TabsTrigger>
                <TabsTrigger value="processing">Processing</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
                <TabsTrigger value="approved">Approved</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      {/* Requests Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      ) : filteredRequests.length === 0 ? (
        <Alert className="bg-slate-900 border-slate-800">
          <Info className="h-4 w-4 text-blue-400" />
          <AlertDescription className="text-slate-300">
            {searchQuery ? 'No explanation requests match your search.' : 'No explanation requests found. Submit one from the AI Gateway!'}
          </AlertDescription>
        </Alert>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredRequests.map((request, index) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <ExplanationRequestCard
                  request={request}
                  onViewDetails={handleViewDetails}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Show count */}
      {!loading && filteredRequests.length > 0 && (
        <div className="text-center text-slate-500 text-sm">
          Showing {filteredRequests.length} of {requests.length} requests
        </div>
      )}
    </div>
  );
};

export default ExplanationRequestsSection;
