import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Brain,
  Calculator,
  FileText,
  TrendingUp,
  Clock,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { useGateway } from '@/hooks/useGateway';
import { useMeTTa } from '@/hooks/useMeTTa';
import { toast } from 'sonner';
import { proposalsAPI } from '@/services/api';

/**
 * Enhanced ProposalCard with AI integration
 * Supports MeTTa priority calculation and Gateway AI analysis
 */
const ProposalCard = ({ 
  id,
  title, 
  status, 
  type, 
  date,
  description,
  metrics = {},
  onViewDetails,
  onUpdate
}) => {
  const [loadingAction, setLoadingAction] = useState(null);
  const { calculatePriority, loading: mettaLoading } = useMeTTa();
  const { requestAllocation, loading: gatewayLoading } = useGateway();
  const statusColors = {
    'pending': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    'in_review': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    'approved': 'bg-green-500/20 text-green-400 border-green-500/30',
    'rejected': 'bg-red-500/20 text-red-400 border-red-500/30',
    'expired': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  const typeColors = {
    'allocation': 'bg-violet-500/20 text-violet-400',
    'governance': 'bg-indigo-500/20 text-indigo-400',
    'infrastructure': 'bg-cyan-500/20 text-cyan-400',
    'community': 'bg-pink-500/20 text-pink-400',
  };

  /**
   * Calculate priority using MeTTa engine
   */
  const handleCalculatePriority = async (e) => {
    e.stopPropagation();
    setLoadingAction('priority');

    try {
      const data = {
        poverty_index: metrics.poverty_index || 0.5,
        project_impact: metrics.project_impact || 0.6,
        deforestation: metrics.deforestation || 0.4,
        corruption_risk: metrics.corruption_risk || 0.3,
      };

      const result = await calculatePriority(data);
      toast.success(`Priority Score: ${result.priority_score?.toFixed(2)}`);
      
      if (onUpdate) {
        onUpdate({ ...result, id });
      }
    } catch (error) {
      console.error('Priority calculation failed:', error);
    } finally {
      setLoadingAction(null);
    }
  };

  /**
   * Request AI analysis using Gateway
   */
  const handleRequestAnalysis = async (e) => {
    e.stopPropagation();
    setLoadingAction('analysis');

    try {
      const data = {
        region_id: id || 'proposal_' + Date.now(),
        project_name: title,
        metrics: JSON.stringify(metrics),
        type: type,
      };

      const result = await requestAllocation(data);
      toast.success('AI analysis requested successfully');
      
      if (onUpdate) {
        onUpdate({ ...result, id });
      }
    } catch (error) {
      console.error('AI analysis request failed:', error);
    } finally {
      setLoadingAction(null);
    }
  };

  /**
   * Vote on proposal
   */
  const handleVote = async (voteType, e) => {
    e.stopPropagation();
    setLoadingAction(`vote_${voteType}`);

    try {
      if (id) {
        await proposalsAPI.vote(id, { vote_type: voteType });
        toast.success(`Vote ${voteType} submitted`);
        
        if (onUpdate) {
          onUpdate({ id });
        }
      }
    } catch (error) {
      console.error('Vote failed:', error);
      toast.error('Failed to submit vote');
    } finally {
      setLoadingAction(null);
    }
  };

  const isLoading = mettaLoading || gatewayLoading || loadingAction;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      <Card 
        className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-all cursor-pointer group"
        onClick={() => onViewDetails && onViewDetails(id)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between mb-2">
            <div className="flex gap-2">
              <Badge 
                variant="outline" 
                className={statusColors[status?.toLowerCase()] || statusColors['pending']}
              >
                <Clock className="w-3 h-3 mr-1" />
                {status || 'Pending'}
              </Badge>
              {type && (
                <Badge 
                  variant="secondary" 
                  className={typeColors[type.toLowerCase()] || 'bg-slate-500/20 text-slate-400'}
                >
                  {type}
                </Badge>
              )}
            </div>
            <ChevronRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform" />
          </div>
          <CardTitle className="text-white text-lg group-hover:text-violet-400 transition-colors">
            {title || 'Untitled Proposal'}
          </CardTitle>
          {description && (
            <CardDescription className="text-slate-400 line-clamp-2">
              {description}
            </CardDescription>
          )}
        </CardHeader>
        
        <CardContent className="space-y-3">
          {/* Metrics Display */}
          {metrics && Object.keys(metrics).length > 0 && (
            <div className="grid grid-cols-2 gap-2 p-2 bg-slate-900/50 rounded-md">
              {Object.entries(metrics).slice(0, 4).map(([key, value]) => (
                <div key={key} className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-violet-400" />
                  <span className="text-xs text-slate-400">
                    {key.replace('_', ' ')}: 
                  </span>
                  <span className="text-xs text-white font-medium">
                    {typeof value === 'number' ? value.toFixed(2) : value}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Date */}
          {date && (
            <p className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {date}
            </p>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCalculatePriority}
              disabled={isLoading}
              className="flex-1 bg-slate-900 border-slate-700 hover:bg-slate-800 hover:border-violet-600"
            >
              {loadingAction === 'priority' ? (
                <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              ) : (
                <Calculator className="w-3 h-3 mr-1" />
              )}
              Priority
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleRequestAnalysis}
              disabled={isLoading}
              className="flex-1 bg-slate-900 border-slate-700 hover:bg-slate-800 hover:border-violet-600"
            >
              {loadingAction === 'analysis' ? (
                <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              ) : (
                <Brain className="w-3 h-3 mr-1" />
              )}
              AI Analysis
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ProposalCard;
