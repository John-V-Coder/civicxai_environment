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
  Info,
  Brain,
  ArrowLeft,
  Upload,
  X,
  Copy,
  Download,
  Share2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useGateway } from '@/hooks/useGateway';
import { toast } from 'sonner';
import { explanationRequestsAPI } from '@/services/api';

const ExplanationRequest = () => {
  const navigate = useNavigate();
  const { 
    requestExplanation, 
    pollStatus, 
    loading, 
    polling,
    error 
  } = useGateway();

  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [requestId, setRequestId] = useState(null);

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

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const downloadAsText = (text) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `explanation-${explanationForm.region_id || 'export'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Downloaded!');
  };

  const handleExplanationSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    setRequestId(null);

    try {
      // Validate and parse allocation_data JSON
      let allocationData = {};
      if (explanationForm.allocation_data && explanationForm.allocation_data.trim()) {
        try {
          allocationData = JSON.parse(explanationForm.allocation_data);
        } catch (jsonError) {
          toast.error('Invalid JSON in Allocation Data field. Please enter valid JSON format.', {
            duration: 5000
          });
          console.error('JSON Parse Error:', jsonError);
          console.error('Attempted to parse:', explanationForm.allocation_data);
          return;
        }
      }
      
      const data = {
        region_id: explanationForm.region_id,
        allocation_data: allocationData,
        context: explanationForm.context,
        language: explanationForm.language,
        notes: explanationForm.notes
      };

      // Save explanation request to database first
      const savedRequest = await explanationRequestsAPI.create({
        region_id: data.region_id,
        region_name: data.region_id,
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

  const getExplanationText = () => {
    if (!result?.explanation) return '';
    return typeof result.explanation === 'string' ? result.explanation : result.explanation.text;
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
                <Brain className="h-6 w-6 text-purple-500" />
                Explanation Generator
              </h1>
              <p className="text-xs text-slate-500">Generate citizen-friendly explanations</p>
            </div>
          </div>
        </div>

        {/* Request Status Bar */}
        {requestId && polling && (
          <Alert className="mb-4 bg-purple-900/20 border-purple-700">
            <Loader2 className="h-4 w-4 animate-spin" />
            <AlertDescription className="flex items-center justify-between">
              <span>Generating explanation: <code className="text-xs">{requestId}</code></span>
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

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {/* Left Column - Compact Form (2 columns) */}
          <div className="lg:col-span-2 space-y-4">
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-white">Request Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label className="text-slate-400 text-xs">Region ID *</Label>
                  <Input
                    value={explanationForm.region_id}
                    onChange={(e) => setExplanationForm({...explanationForm, region_id: e.target.value})}
                    placeholder="e.g., REG-001"
                    className="bg-slate-800 border-slate-700 text-white h-9 mt-1"
                    required
                  />
                </div>

                <div>
                  <Label className="text-slate-400 text-xs">Allocation Data (JSON) *</Label>
                  <Textarea
                    value={explanationForm.allocation_data}
                    onChange={(e) => setExplanationForm({...explanationForm, allocation_data: e.target.value})}
                    placeholder='{"poverty_index": 0.85, "priority_score": 0.78}'
                    className="bg-slate-800 border-slate-700 text-white font-mono text-xs mt-1"
                    rows={4}
                  />
                  <p className="text-[10px] text-slate-600 mt-1">
                    Must be valid JSON format
                  </p>
                </div>

                <div>
                  <Label className="text-slate-400 text-xs">Context</Label>
                  <Textarea
                    value={explanationForm.context}
                    onChange={(e) => setExplanationForm({...explanationForm, context: e.target.value})}
                    placeholder="Why this region received this allocation..."
                    className="bg-slate-800 border-slate-700 text-white text-sm mt-1"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-slate-400 text-xs">Language</Label>
                    <Input
                      value={explanationForm.language}
                      onChange={(e) => setExplanationForm({...explanationForm, language: e.target.value})}
                      placeholder="en"
                      className="bg-slate-800 border-slate-700 text-white h-9 text-sm mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <label className="w-full">
                      <div className="flex items-center justify-center h-9 border border-slate-700 rounded-lg cursor-pointer hover:border-purple-500 transition-colors bg-slate-800">
                        <Upload className="h-3 w-3 text-slate-500 mr-1.5" />
                        <span className="text-xs text-slate-400">Upload</span>
                      </div>
                      <input
                        type="file"
                        multiple
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>

                {files.length > 0 && (
                  <div className="space-y-1.5">
                    {files.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-1.5 bg-slate-800 rounded border border-slate-700">
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <FileText className="h-3 w-3 text-purple-400 flex-shrink-0" />
                          <span className="text-xs text-slate-300 truncate">{file.name}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeFile(index)}
                          className="h-6 w-6 text-slate-400 hover:text-red-400"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                <div>
                  <Label className="text-slate-400 text-xs">Notes (Optional)</Label>
                  <Textarea
                    value={explanationForm.notes}
                    onChange={(e) => setExplanationForm({...explanationForm, notes: e.target.value})}
                    placeholder="Additional information..."
                    className="bg-slate-800 border-slate-700 text-white text-sm mt-1"
                    rows={2}
                  />
                </div>

                <Button
                  onClick={handleExplanationSubmit}
                  disabled={loading || polling || !explanationForm.region_id}
                  className="w-full bg-purple-600 hover:bg-purple-700 h-10"
                >
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {polling && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {!loading && !polling && <Sparkles className="mr-2 h-4 w-4" />}
                  {loading ? 'Submitting...' : polling ? 'Generating...' : 'Generate Explanation'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Explanation Display (3 columns) */}
          <div className="lg:col-span-3 space-y-4">
            {result && result.explanation ? (
              <>
                {/* Main Explanation Text - Large and Prominent */}
                <Card className="bg-slate-900/50 border-slate-800">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base text-white flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Generated Explanation
                      </CardTitle>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(getExplanationText())}
                          className="h-8 text-slate-400 hover:text-white"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => downloadAsText(getExplanationText())}
                          className="h-8 text-slate-400 hover:text-white"
                        >
                          <Download className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-700/30 rounded-lg p-6">
                      <p className="text-slate-200 text-base leading-relaxed whitespace-pre-wrap">
                        {getExplanationText()}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Additional Information - Compact Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Key Points */}
                  {result.explanation.key_points && result.explanation.key_points.length > 0 && (
                    <Card className="bg-slate-900/50 border-slate-800">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-white">Key Points</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {result.explanation.key_points.map((point, i) => (
                            <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                              <CheckCircle2 className="h-3 w-3 mt-0.5 text-green-500 flex-shrink-0" />
                              <span>{point}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}

                  {/* Transparency Score */}
                  {result.explanation.transparency_score !== undefined && (
                    <Card className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-700">
                      <CardContent className="pt-6">
                        <div className="text-center">
                          <p className="text-xs text-slate-400 mb-2">Transparency Score</p>
                          <p className="text-4xl font-bold text-purple-400">
                            {(result.explanation.transparency_score * 100).toFixed(1)}%
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Policy Implications */}
                  {result.explanation.policy_implications && result.explanation.policy_implications.length > 0 && (
                    <Card className="bg-slate-900/50 border-slate-800 md:col-span-2">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm text-white">Policy Implications</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-2">
                          {result.explanation.policy_implications.map((implication, i) => (
                            <div key={i} className="bg-purple-900/20 p-3 rounded border border-purple-700/50">
                              <p className="text-xs text-slate-300">{implication}</p>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Raw JSON - Collapsed by default */}
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
              /* Empty State - Guidance */
              <Card className="bg-slate-900/50 border-slate-800 h-full">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="p-4 rounded-full bg-purple-500/20 mb-4">
                      <Brain className="h-12 w-12 text-purple-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">
                      AI Explanation Generator
                    </h3>
                    <p className="text-sm text-slate-400 mb-6 max-w-md">
                      Generate clear, citizen-friendly explanations for allocation decisions that improve transparency and build trust.
                    </p>
                    
                    {loading || polling ? (
                      <div className="bg-purple-900/20 rounded-lg p-6 border border-purple-700 w-full max-w-md">
                        <div className="flex items-center gap-3 mb-3">
                          <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
                          <div className="flex-1 text-left">
                            <p className="text-sm text-white font-medium">
                              {loading ? 'Submitting Request' : 'Generating Explanation'}
                            </p>
                            {requestId && (
                              <p className="text-xs text-slate-400 mt-0.5">ID: {requestId}</p>
                            )}
                          </div>
                        </div>
                        <Progress value={undefined} className="h-1.5" />
                      </div>
                    ) : error ? (
                      <Alert className="bg-orange-900/20 border-orange-700 max-w-md">
                        <XCircle className="h-4 w-4 text-orange-400" />
                        <AlertDescription className="text-xs text-slate-300">
                          {error}
                        </AlertDescription>
                      </Alert>
                    ) : (
                      <div className="bg-slate-800/50 rounded-lg p-4 w-full max-w-md">
                        <p className="text-xs text-slate-500 mb-3">What you'll get:</p>
                        <ul className="space-y-2 text-left">
                          <li className="flex items-center gap-2 text-xs text-slate-400">
                            <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                            Clear, jargon-free explanation
                          </li>
                          <li className="flex items-center gap-2 text-xs text-slate-400">
                            <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                            Key decision points highlighted
                          </li>
                          <li className="flex items-center gap-2 text-xs text-slate-400">
                            <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                            Policy implications identified
                          </li>
                          <li className="flex items-center gap-2 text-xs text-slate-400">
                            <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                            Transparency score calculated
                          </li>
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExplanationRequest;