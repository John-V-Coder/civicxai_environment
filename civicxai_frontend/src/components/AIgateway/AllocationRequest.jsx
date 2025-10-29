import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Loader2, 
  Sparkles, 
  CheckCircle2, 
  XCircle,
  TrendingUp,
  Brain,
  ArrowLeft,
  Upload,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useGateway } from '@/hooks/useGateway';
import { toast } from 'sonner';
import { allocationRequestsAPI } from '@/services/api';

const AllocationRequest = () => {
  const navigate = useNavigate();
  const { 
    requestAllocation, 
    pollStatus, 
    loading, 
    polling,
    error 
  } = useGateway();

  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [requestId, setRequestId] = useState(null);

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

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    toast.success(`${selectedFiles.length} file(s) selected`);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
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
        region_name: data.region_id,
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900">
      <div className="container mx-auto p-4 max-w-7xl">
        {/* Compact Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => navigate('/ai-gateway')}
              className="text-slate-400 hover:text-white"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Brain className="h-6 w-6 text-blue-500" />
                Allocation Request
              </h1>
              <p className="text-xs text-slate-500">AI-powered allocation analysis</p>
            </div>
          </div>

        </div>

        {/* Request Status Bar */}
        {requestId && polling && (
          <Alert className="mb-4 bg-blue-900/20 border-blue-700">
            <Loader2 className="h-4 w-4 animate-spin" />
            <AlertDescription className="flex items-center justify-between">
              <span>Processing request: <code className="text-xs">{requestId}</code></span>
              <Progress value={undefined} className="w-32 h-2" />
            </AlertDescription>
          </Alert>
        )}

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mb-4">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Left Column - Form */}
          <div className="lg:col-span-2 space-y-4">
            {/* Basic Info Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-white">Region Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="col-span-2">
                    <Label className="text-slate-400 text-xs">Region ID *</Label>
                    <Input
                      value={allocationForm.region_id}
                      onChange={(e) => setAllocationForm({...allocationForm, region_id: e.target.value})}
                      placeholder="e.g., REG-001"
                      className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                      required
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Metrics Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-white">Key Metrics</CardTitle>
                <CardDescription className="text-xs">Values between 0 and 1</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-slate-400 text-xs">Poverty Index</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.poverty_index}
                      onChange={(e) => setAllocationForm({...allocationForm, poverty_index: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">Project Impact</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.project_impact}
                      onChange={(e) => setAllocationForm({...allocationForm, project_impact: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">Environmental Score</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.environmental_score}
                      onChange={(e) => setAllocationForm({...allocationForm, environmental_score: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">Corruption Risk</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={allocationForm.corruption_risk}
                      onChange={(e) => setAllocationForm({...allocationForm, corruption_risk: e.target.value})}
                      className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                      required
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Additional Info Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-white">Additional Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label className="text-slate-400 text-xs">Notes (Optional)</Label>
                  <Textarea
                    value={allocationForm.notes}
                    onChange={(e) => setAllocationForm({...allocationForm, notes: e.target.value})}
                    placeholder="Any additional context..."
                    className="bg-slate-800 border-slate-700 text-white text-sm mt-1"
                    rows={3}
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs">Reference URLs (Optional)</Label>
                  <Input
                    value={allocationForm.urls}
                    onChange={(e) => setAllocationForm({...allocationForm, urls: e.target.value})}
                    placeholder="Comma-separated URLs"
                    className="bg-slate-800 border-slate-700 text-white h-9 text-sm mt-1"
                  />
                </div>
              </CardContent>
            </Card>

            {/* File Upload Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-white">Documents</CardTitle>
                <CardDescription className="text-xs">Upload PDFs, images, or data files</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <label className="flex items-center justify-center w-full h-24 border-2 border-dashed border-slate-700 rounded-lg cursor-pointer hover:border-blue-500 transition-colors bg-slate-800/50">
                    <div className="text-center">
                      <Upload className="h-6 w-6 text-slate-500 mx-auto mb-2" />
                      <p className="text-sm text-slate-400">Click to upload files</p>
                      <p className="text-xs text-slate-600">PDF, PNG, JPG, TXT, CSV</p>
                    </div>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.png,.jpg,.jpeg,.txt,.csv"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>

                  {/* File List */}
                  {files.length > 0 && (
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-slate-800 rounded border border-slate-700">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <FileText className="h-4 w-4 text-blue-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-slate-300 truncate">{file.name}</p>
                              <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeFile(index)}
                            className="h-7 w-7 text-slate-400 hover:text-red-400"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Results */}
          <div className="space-y-4">
            {result && result.recommendation ? (
              <>
                {/* Priority Card */}
                <Card className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 border-blue-700">
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <CheckCircle2 className="h-12 w-12 text-green-400 mx-auto mb-3" />
                      <p className="text-xs text-slate-400 mb-2">Priority Level</p>
                      <Badge className="text-lg px-4 py-1 bg-blue-600">
                        {result.recommendation.priority_level?.toUpperCase()}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>

                {/* Metrics Cards */}
                <div className="grid grid-cols-2 gap-3">
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardContent className="pt-4">
                      <p className="text-xs text-slate-500 mb-1">Confidence</p>
                      <p className="text-xl font-bold text-white">
                        {(result.recommendation.confidence_score * 100).toFixed(1)}%
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardContent className="pt-4">
                      <p className="text-xs text-slate-500 mb-1">Allocation</p>
                      <p className="text-xl font-bold text-blue-400">
                        {result.recommendation.recommended_allocation_percentage}%
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Key Findings */}
                {result.recommendation.key_findings && result.recommendation.key_findings.length > 0 && (
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-white">Key Findings</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {result.recommendation.key_findings.map((finding, i) => (
                          <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                            <TrendingUp className="h-3 w-3 mt-0.5 text-green-500 flex-shrink-0" />
                            <span>{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Recommendations */}
                {result.recommendation.recommendations && result.recommendation.recommendations.length > 0 && (
                  <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm text-white">Recommendations</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {result.recommendation.recommendations.map((rec, i) => (
                          <li key={i} className="bg-blue-900/20 p-2 rounded border border-blue-800">
                            <p className="text-xs text-blue-400 mb-1">{rec.type}</p>
                            <p className="text-xs text-slate-300">{rec.action}</p>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Raw Data */}
                <details className="bg-slate-900/50 border border-slate-800 rounded-lg">
                  <summary className="p-3 text-xs text-slate-400 cursor-pointer hover:text-white">
                    View Raw Response
                  </summary>
                  <pre className="p-3 text-[10px] text-slate-500 overflow-auto max-h-64">
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </details>
              </>
            ) : (
              /* Analysis Card - Always Visible */
              <Card className="bg-slate-900/50 border-slate-800 sticky top-4">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base text-white flex items-center gap-2">
                    <Brain className="h-5 w-5 text-blue-500" />
                    AI Analysis
                  </CardTitle>
                  <CardDescription className="text-xs">
                    {loading ? 'Submitting request...' : polling ? 'Processing analysis...' : 'Ready to analyze your allocation request'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Analysis Button */}
                  <Button
                    onClick={handleAllocationSubmit}
                    disabled={loading || polling || !allocationForm.region_id}
                    className="w-full bg-blue-600 hover:bg-blue-700 h-11"
                    size="lg"
                  >
                    {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {polling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    {!loading && !polling && <Sparkles className="mr-2 h-5 w-5" />}
                    {loading ? 'Submitting...' : polling ? 'Processing...' : 'Run AI Analysis'}
                  </Button>

                  {/* Status Info */}
                  {!loading && !polling && !error && (
                    <div className="bg-slate-800/50 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/20">
                          <Brain className="h-4 w-4 text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-slate-300 mb-1 font-medium">What happens next?</p>
                          <ul className="space-y-1.5 text-xs text-slate-500">
                            <li className="flex items-center gap-2">
                              <div className="h-1 w-1 rounded-full bg-blue-500"></div>
                              Request saved to dashboard
                            </li>
                            <li className="flex items-center gap-2">
                              <div className="h-1 w-1 rounded-full bg-blue-500"></div>
                              AI Gateway processes data
                            </li>
                            <li className="flex items-center gap-2">
                              <div className="h-1 w-1 rounded-full bg-blue-500"></div>
                              MeTTa calculates priority score
                            </li>
                            <li className="flex items-center gap-2">
                              <div className="h-1 w-1 rounded-full bg-blue-500"></div>
                              Results appear here
                            </li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Processing Status */}
                  {(loading || polling) && (
                    <div className="bg-blue-900/20 rounded-lg p-4 border border-blue-800">
                      <div className="flex items-center gap-3 mb-3">
                        <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                        <div className="flex-1">
                          <p className="text-sm text-white font-medium">
                            {loading ? 'Submitting Request' : 'AI Processing'}
                          </p>
                          {requestId && (
                            <p className="text-xs text-slate-400 mt-0.5">ID: {requestId}</p>
                          )}
                        </div>
                      </div>
                      <Progress value={undefined} className="h-1.5" />
                    </div>
                  )}

                  {/* Gateway Error State */}
                  {error && error.includes('Gateway') && (
                    <Alert className="bg-orange-900/20 border-orange-700">
                      <XCircle className="h-4 w-4 text-orange-400" />
                      <AlertDescription className="text-xs text-slate-300">
                        <p className="font-medium mb-2">AI Gateway Unavailable</p>
                        <p className="text-slate-400 mb-3">The AI Gateway service is not running. Your request has been saved to the dashboard.</p>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="h-8 text-xs"
                            onClick={() => navigate('/dashboard')}
                          >
                            View Dashboard
                          </Button>
                          <Button 
                            size="sm"
                            className="h-8 text-xs bg-orange-600 hover:bg-orange-700"
                            onClick={() => window.location.reload()}
                          >
                            Retry
                          </Button>
                        </div>
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* General Error State */}
                  {error && !error.includes('Gateway') && (
                    <Alert variant="destructive">
                      <XCircle className="h-4 w-4" />
                      <AlertDescription className="text-xs">
                        {error}
                      </AlertDescription>
                    </Alert>
                  )}

                  {/* Quick Tips */}
                  {!loading && !polling && !error && (
                    <div className="border-t border-slate-800 pt-4">
                      <p className="text-xs text-slate-500 mb-2 font-medium">💡 Tips for better results:</p>
                      <ul className="space-y-1 text-xs text-slate-600">
                        <li>• Upload relevant PDFs for context</li>
                        <li>• Ensure metrics are accurate</li>
                        <li>• Add detailed notes if available</li>
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllocationRequest;