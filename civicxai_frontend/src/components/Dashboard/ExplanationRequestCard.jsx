import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  Activity,
  Sparkles,
  ChevronRight,
  MessageSquare,
  Shield,
  BookOpen,
  Globe
} from 'lucide-react';

/**
 * Beautiful card for displaying explanation requests from AI Gateway
 * Shows region name and explanation details
 */
const ExplanationRequestCard = ({ 
  request,
  onViewDetails,
  compact = false
}) => {
  // Status configurations
  const statusConfig = {
    'pending': {
      color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      icon: Clock,
      label: 'Pending'
    },
    'processing': {
      color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      icon: Activity,
      label: 'Processing'
    },
    'completed': {
      color: 'bg-green-500/20 text-green-400 border-green-500/30',
      icon: CheckCircle2,
      label: 'Completed'
    },
    'approved': {
      color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      icon: CheckCircle2,
      label: 'Approved'
    },
    'rejected': {
      color: 'bg-red-500/20 text-red-400 border-red-500/30',
      icon: AlertCircle,
      label: 'Rejected'
    }
  };

  const currentStatus = statusConfig[request.status] || statusConfig['pending'];
  const StatusIcon = currentStatus.icon;

  // Language icons
  const languageIcons = {
    'technical': BookOpen,
    'simple': MessageSquare,
    'policy': Shield,
  };

  const LanguageIcon = languageIcons[request.language] || Globe;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className="w-full"
    >
      <Card 
        className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border-slate-700 hover:border-blue-500/50 transition-all cursor-pointer group backdrop-blur-sm"
        onClick={() => onViewDetails && onViewDetails(request)}
      >
        <CardHeader className="pb-3">
          {/* Header with Region Name and Status */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2.5 rounded-lg bg-blue-500/20 border border-blue-500/30 group-hover:bg-blue-500/30 transition-colors">
                <FileText className="h-5 w-5 text-blue-400" />
              </div>
              <div className="flex-1">
                <CardTitle className="text-white text-xl font-bold group-hover:text-blue-400 transition-colors flex items-center gap-2">
                  {request.region_name || request.region_id}
                  {request.files_attached > 0 && (
                    <Badge variant="outline" className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">
                      <FileText className="h-3 w-3 mr-1" />
                      {request.files_attached} files
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription className="text-slate-400 text-sm mt-0.5">
                  Explanation Request: {request.region_id}
                </CardDescription>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-2">
              <Badge variant="outline" className={currentStatus.color}>
                <StatusIcon className="w-3 h-3 mr-1" />
                {currentStatus.label}
              </Badge>
              <ChevronRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 group-hover:text-blue-400 transition-all" />
            </div>
          </div>

          {/* Language Badge */}
          <div className="flex items-center gap-2 mt-2">
            <Badge className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30 border-0 font-medium text-sm px-3 py-1">
              <LanguageIcon className="w-3 h-3 mr-1" />
              {request.language.charAt(0).toUpperCase() + request.language.slice(1)} Language
            </Badge>
            {request.transparency_score !== null && request.transparency_score !== undefined && (
              <span className="text-xs text-slate-400">
                Transparency: {(request.transparency_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Context (if available) */}
          {request.context && !compact && (
            <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-800">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide mb-2 flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                Context
              </p>
              <p className="text-sm text-slate-400 line-clamp-3">
                {request.context}
              </p>
            </div>
          )}

          {/* Explanation Text (if available) */}
          {request.explanation_text && !compact && (
            <div className="p-4 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-lg border border-blue-500/30">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                <span className="text-sm font-medium text-slate-300">AI Generated Explanation</span>
              </div>
              <p className="text-sm text-slate-300 line-clamp-4">
                {request.explanation_text}
              </p>
            </div>
          )}

          {/* Key Points (if available) */}
          {request.key_points && request.key_points.length > 0 && !compact && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-green-400" />
                Key Points
              </p>
              <div className="space-y-1">
                {request.key_points.slice(0, 3).map((point, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-400 bg-slate-800/30 p-2 rounded">
                    <span className="text-blue-400 font-bold">•</span>
                    <span className="flex-1">{point}</span>
                  </div>
                ))}
                {request.key_points.length > 3 && (
                  <p className="text-xs text-slate-500 italic">
                    +{request.key_points.length - 3} more points
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Policy Implications (if available) */}
          {request.policy_implications && request.policy_implications.length > 0 && !compact && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide flex items-center gap-1">
                <Shield className="w-3 h-3 text-indigo-400" />
                Policy Implications
              </p>
              <div className="space-y-1">
                {request.policy_implications.slice(0, 2).map((implication, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-400 bg-indigo-900/20 p-2 rounded border border-indigo-500/20">
                    <span className="text-indigo-400 font-bold">▸</span>
                    <span className="flex-1">{implication}</span>
                  </div>
                ))}
                {request.policy_implications.length > 2 && (
                  <p className="text-xs text-slate-500 italic">
                    +{request.policy_implications.length - 2} more implications
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Notes (if available) */}
          {request.notes && !compact && (
            <div className="pt-2 border-t border-slate-800">
              <p className="text-xs text-slate-500 line-clamp-2">
                {request.notes}
              </p>
            </div>
          )}

          {/* Timestamp */}
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(request.created_at).toLocaleDateString()} at {new Date(request.created_at).toLocaleTimeString()}
            </span>
            {request.completed_at && (
              <span className="flex items-center gap-1 text-green-400">
                <CheckCircle2 className="w-3 h-3" />
                Completed
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ExplanationRequestCard;
