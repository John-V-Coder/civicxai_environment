import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Upload, 
  FileText, 
  Loader2, 
  Sparkles, 
  CheckCircle2, 
  XCircle,
  Info,
  TrendingUp,
  Brain,
  Network,
  MessageCircle
} from 'lucide-react';
import { useGateway } from '@/hooks/useGateway';
import { toast } from 'sonner';
import AIGatewayChat from './AIGatewayChat';
import { allocationRequestsAPI, explanationRequestsAPI } from '@/services/api';

const AIGateway = () => {
  const { 
    requestAllocation, 
    requestExplanation, 
    pollStatus, 
    checkHealth,
    getMetrics,
    loading, 
    polling,
    error 
  } = useGateway();

  const [activeTab, setActiveTab] = useState('chat');
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [requestId, setRequestId] = useState(null);
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);

  // Allocation form state
  const [allocationForm, setAllocationForm] = useState({
    region_id: '',
    poverty_index: '0.85',
    project_impact: '0.90',
    environmental_score: '0.75',
    corruption_risk: '0.30',
    notes: '',
    urls: ''
  });

  // Explanation form state
  const [explanationForm, setExplanationForm] = useState({
    region_id: '',
    allocation_data: '',
    context: '',
    language: 'en',
    notes: ''
  });

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    toast.success(`${selectedFiles.length} file(s) selected`);
  };

  const handleAllocationSubmit = async (e) => {
    e.preventDefault();
    
    // Validate region ID is not empty
    if (!allocationForm.region_id || allocationForm.region_id.trim() === '') {
      toast.error('Please enter a Region ID before submitting');
      return;
    }
    
    setResult(null);
    setRequestId(null);

    try {
      // Convert form data to proper types
      const data = {
        region_id: allocationForm.region_id,
        poverty_index: parseFloat(allocationForm.poverty_index),
        project_impact: parseFloat(allocationForm.project_impact),
        environmental_score: parseFloat(allocationForm.environmental_score),
        corruption_risk: parseFloat(allocationForm.corruption_risk),
        notes: allocationForm.notes,
        urls: allocationForm.urls
      };

      // Save allocation request to database first
      const savedRequest = await allocationRequestsAPI.create({
        region_id: data.region_id,
        region_name: data.region_id, // Will be displayed as title
        poverty_index: data.poverty_index,
        project_impact: data.project_impact,
        environmental_score: data.environmental_score,
        corruption_risk: data.corruption_risk,
        notes: data.notes,
        urls: data.urls,
        files_attached: files.length,
        status: 'processing'
      });

      toast.success('Allocation request saved to dashboard!');

      // Submit request to Gateway for AI analysis
      const response = await requestAllocation(data, files);
      setRequestId(response.request_id);
      toast.success('Request submitted to AI Gateway');

      // Start polling for results
      const finalResult = await pollStatus(response.request_id, {
        maxAttempts: 30,
        interval: 2000,
        onUpdate: (status) => {
          console.log('Status update:', status.status);
        }
      });

      // Update the saved request with AI results
      if (finalResult && savedRequest.data?.request_id) {
        await allocationRequestsAPI.update(savedRequest.data.request_id, {
          status: 'analyzed',
          priority_level: finalResult.recommendation?.priority_level,
          confidence_score: finalResult.recommendation?.confidence_score,
          recommended_allocation_percentage: finalResult.recommendation?.recommended_allocation_percentage,
          ai_recommendation: finalResult.recommendation?.rationale,
          key_findings: finalResult.recommendation?.key_findings || [],
          recommendations: finalResult.recommendation?.recommendations || []
        });
      }

      setResult(finalResult);
      toast.success('AI analysis completed and saved!');
    } catch (err) {
      console.error('Allocation request error:', err);
      console.error('Error response:', err.response?.data);
      
      // Handle gateway not running
      if (err.response?.status === 503) {
        toast.error('AI Gateway is not running. Please start the gateway server or use the MeTTa Calculator instead.', {
          duration: 5000
        });
        return;
      }
      
      // Handle database save errors (400)
      if (err.response?.status === 400 && err.response?.data) {
        const errorData = err.response.data;
        const errorMessage = errorData.error || errorData.message || 'Failed to save allocation request';
        toast.error(`Error: ${errorMessage}`, {
          duration: 5000
        });
        
        // Log detailed error for debugging
        if (errorData.traceback) {
          console.error('Backend traceback:', errorData.traceback);
        }
        if (errorData.received_data) {
          console.error('Data received by backend:', errorData.received_data);
        }
        return;
      }
      
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to complete AI analysis';
      toast.error(errorMessage);
    }
  };

  const handleExplanationSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setRequestId(null);

    try {
      // Parse allocation_data JSON
      const data = {
        region_id: explanationForm.region_id,
        allocation_data: explanationForm.allocation_data ? 
          JSON.parse(explanationForm.allocation_data) : {},
        context: explanationForm.context,
        language: explanationForm.language,
        notes: explanationForm.notes
      };

      // Save explanation request to database first
      const savedRequest = await explanationRequestsAPI.create({
        region_id: data.region_id,
        region_name: data.region_id, // Will be displayed as title
        allocation_data: data.allocation_data,
        context: data.context,
        language: data.language,
        notes: data.notes,
        files_attached: files.length,
        status: 'processing'
      });

      toast.success('Explanation request saved to dashboard!');

      // Submit request to Gateway for AI processing
      const response = await requestExplanation(data, files);
      setRequestId(response.request_id);
      toast.success('Explanation request submitted');

      // Poll for results
      const finalResult = await pollStatus(response.request_id, {
        maxAttempts: 30,
        interval: 2000,
        onUpdate: (status) => {
          console.log('Status update:', status.status);
        }
      });

      // Update the saved request with AI results
      if (finalResult && savedRequest.data?.request_id) {
        await explanationRequestsAPI.update(savedRequest.data.request_id, {
          status: 'completed',
          explanation_text: finalResult.explanation?.text || '',
          key_points: finalResult.explanation?.key_points || [],
          policy_implications: finalResult.explanation?.policy_implications || [],
          transparency_score: finalResult.explanation?.transparency_score || 0
        });
      }

      setResult(finalResult);
      toast.success('Explanation generated and saved!');
    } catch (err) {
      console.error('Explanation request error:', err);
      
      // Handle gateway not running
      if (err.response?.status === 503) {
        toast.error('AI Gateway is not running. Please start the gateway server or use the MeTTa Calculator instead.', {
          duration: 5000
        });
        return;
      }
      
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to generate explanation';
      toast.error(errorMessage);
    }
  };

  const handleHealthCheck = async () => {
    const healthStatus = await checkHealth();
    setHealth(healthStatus);
  };

  const handleGetMetrics = async () => {
    const metricsData = await getMetrics();
    setMetrics(metricsData);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Network className="h-8 w-8 text-blue-500" />
            AI Gateway
          </h1>
          <p className="text-slate-400 mt-1">
            Advanced AI analysis with PDF processing powered by uAgents
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleHealthCheck} disabled={loading}>
            Check Health
          </Button>
          <Button variant="outline" onClick={handleGetMetrics} disabled={loading}>
            Get Metrics
          </Button>
        </div>
      </div>

      {/* Health & Metrics Status */}
      {health && (
        <Alert className="bg-slate-900 border-slate-700">
          <CheckCircle2 className="h-4 w-4 text-green-500" />
          <AlertDescription className="text-slate-300">
            Gateway Status: <Badge variant="success">{health.gateway_status}</Badge>
            {health.agent_active && <span className="ml-2">• Agent Active</span>}
          </AlertDescription>
        </Alert>
      )}

      {metrics && (
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white">Gateway Metrics</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-slate-400 text-sm">Total Requests</p>
              <p className="text-2xl font-bold text-white">{metrics.metrics?.total_requests || 0}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Pending</p>
              <p className="text-2xl font-bold text-orange-500">{metrics.metrics?.pending_requests || 0}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Completed</p>
              <p className="text-2xl font-bold text-green-500">{metrics.metrics?.completed_requests || 0}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-900">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4" />
            Chat Assistant
          </TabsTrigger>
          <TabsTrigger value="allocation">Allocation Request</TabsTrigger>
          <TabsTrigger value="explanation">Explanation Request</TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-6">
          <AIGatewayChat />
        </TabsContent>

        {/* Allocation Tab */}
        <TabsContent value="allocation" className="space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="h-5 w-5 text-blue-500" />
                AI-Powered Allocation Analysis
              </CardTitle>
              <CardDescription className="text-slate-400">
                Upload PDFs and submit allocation data for advanced AI recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAllocationSubmit} className="space-y-6">
                {/* Region ID */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Region ID</Label>
                  <Input
                    value={allocationForm.region_id}
                    onChange={(e) => setAllocationForm({...allocationForm, region_id: e.target.value})}
                    placeholder="e.g., REG-001"
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-slate-300">Poverty Index (0-1)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.poverty_index}
                      onChange={(e) => setAllocationForm({...allocationForm, poverty_index: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Project Impact (0-1)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.project_impact}
                      onChange={(e) => setAllocationForm({...allocationForm, project_impact: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Environmental Score (0-1)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.environmental_score}
                      onChange={(e) => setAllocationForm({...allocationForm, environmental_score: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">Corruption Risk (0-1)</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.corruption_risk}
                      onChange={(e) => setAllocationForm({...allocationForm, corruption_risk: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white"
                      required
                    />
                  </div>
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Additional Notes (Optional)</Label>
                  <Textarea
                    value={allocationForm.notes}
                    onChange={(e) => setAllocationForm({...allocationForm, notes: e.target.value})}
                    placeholder="Any additional context about this region..."
                    className="bg-slate-800 border-slate-700 text-white"
                    rows={3}
                  />
                </div>

                {/* URLs */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Reference URLs (Optional, comma-separated)</Label>
                  <Input
                    value={allocationForm.urls}
                    onChange={(e) => setAllocationForm({...allocationForm, urls: e.target.value})}
                    placeholder="https://example.com/report1, https://example.com/report2"
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                {/* File Upload */}
                <div className="space-y-2">
                  <Label className="text-slate-300">Upload Documents (PDFs, Images)</Label>
                  <div className="flex items-center gap-4">
                    <Input
                      type="file"
                      multiple
                      accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
                      onChange={handleFileChange}
                      className="bg-slate-800 border-slate-700 text-white"
                    />
                    {files.length > 0 && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        {files.length} file(s)
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-500">
                    Gateway will extract text from PDFs and include in AI analysis
                  </p>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  disabled={loading || polling}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  size="lg"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {polling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {!loading && !polling && <Sparkles className="mr-2 h-4 w-4" />}
                  {loading ? 'Submitting...' : polling ? 'Processing...' : 'Submit to AI Gateway'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Explanation Tab */}
        <TabsContent value="explanation" className="space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-500" />
                AI Explanation Generator
              </CardTitle>
              <CardDescription className="text-slate-400">
                Generate citizen-friendly explanations for allocation decisions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleExplanationSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label className="text-slate-300">Region ID</Label>
                  <Input
                    value={explanationForm.region_id}
                    onChange={(e) => setExplanationForm({...explanationForm, region_id: e.target.value})}
                    placeholder="e.g., REG-001"
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Allocation Data (JSON)</Label>
                  <Textarea
                    value={explanationForm.allocation_data}
                    onChange={(e) => setExplanationForm({...explanationForm, allocation_data: e.target.value})}
                    placeholder='{"priority_score": 0.85, "amount": 5000000}'
                    className="bg-slate-800 border-slate-700 text-white font-mono"
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Context</Label>
                  <Textarea
                    value={explanationForm.context}
                    onChange={(e) => setExplanationForm({...explanationForm, context: e.target.value})}
                    placeholder="Why this region received this allocation..."
                    className="bg-slate-800 border-slate-700 text-white"
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Language</Label>
                  <Input
                    value={explanationForm.language}
                    onChange={(e) => setExplanationForm({...explanationForm, language: e.target.value})}
                    placeholder="en"
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Supporting Documents (Optional)</Label>
                  <Input
                    type="file"
                    multiple
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={handleFileChange}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading || polling}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                  size="lg"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {polling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {!loading && !polling && <Sparkles className="mr-2 h-4 w-4" />}
                  {loading ? 'Submitting...' : polling ? 'Generating...' : 'Generate Explanation'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Request Status */}
      {requestId && polling && (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
              <div className="flex-1">
                <p className="text-white font-semibold">Processing Request</p>
                <p className="text-slate-400 text-sm">Request ID: {requestId}</p>
                <Progress value={undefined} className="mt-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results Display */}
      {result && (
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              AI Analysis Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Allocation Results */}
            {result.recommendation && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="pt-6">
                      <p className="text-slate-400 text-sm mb-1">Priority Level</p>
                      <Badge className="text-lg px-3 py-1">
                        {result.recommendation.priority_level}
                      </Badge>
                    </CardContent>
                  </Card>
                  <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="pt-6">
                      <p className="text-slate-400 text-sm mb-1">Confidence</p>
                      <p className="text-2xl font-bold text-white">
                        {(result.recommendation.confidence_score * 100).toFixed(1)}%
                      </p>
                    </CardContent>
                  </Card>
                </div>

                <div className="bg-slate-800 p-4 rounded-lg">
                  <p className="text-slate-400 text-sm mb-2">Recommended Allocation</p>
                  <p className="text-3xl font-bold text-blue-500">
                    {result.recommendation.recommended_allocation_percentage}%
                  </p>
                </div>

                {result.recommendation.key_findings && (
                  <div>
                    <p className="text-slate-300 font-semibold mb-2">Key Findings:</p>
                    <ul className="space-y-2">
                      {result.recommendation.key_findings.map((finding, i) => (
                        <li key={i} className="flex items-start gap-2 text-slate-400">
                          <TrendingUp className="h-4 w-4 mt-1 text-green-500 flex-shrink-0" />
                          {finding}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.recommendation.recommendations && (
                  <div>
                    <p className="text-slate-300 font-semibold mb-2">Recommendations:</p>
                    <ul className="space-y-2">
                      {result.recommendation.recommendations.map((rec, i) => (
                        <li key={i} className="bg-blue-900/20 p-3 rounded border border-blue-700">
                          <p className="text-sm text-slate-400">{rec.type}</p>
                          <p className="text-white">{rec.action}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Explanation Results */}
            {result.explanation && (
              <Alert className="bg-blue-900/20 border-blue-700">
                <Info className="h-4 w-4 text-blue-400" />
                <AlertDescription className="text-slate-300">
                  {result.explanation}
                </AlertDescription>
              </Alert>
            )}

            {/* Raw JSON */}
            <details className="bg-slate-800 p-4 rounded">
              <summary className="text-slate-300 cursor-pointer font-semibold">
                View Raw Response
              </summary>
              <pre className="mt-2 text-xs text-slate-400 overflow-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AIGateway;
