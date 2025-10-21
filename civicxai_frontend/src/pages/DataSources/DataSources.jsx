import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import {
  Plus,
  FileText,
  Link as LinkIcon,
  Trash2,
  Edit,
  ExternalLink,
  Search,
  Upload,
  TrendingUp,
  Calendar,
  User,
  Tag
} from 'lucide-react';
import { dataSourcesAPI } from '@/services/api';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

/**
 * Data Sources Management Page
 * Add and manage PDFs and website links for AI knowledge base
 */
const DataSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [stats, setStats] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    source_type: 'url',
    category: 'reference',
    url: '',
    file: null,
    author: '',
    published_date: '',
    tags: '',
    summary: '',
    key_points: '',
    is_active: true
  });

  const categories = [
    { value: 'policy', label: 'Policy Document' },
    { value: 'research', label: 'Research Paper' },
    { value: 'data', label: 'Data Source' },
    { value: 'guideline', label: 'Guideline' },
    { value: 'report', label: 'Report' },
    { value: 'reference', label: 'Reference Material' },
    { value: 'other', label: 'Other' }
  ];

  const sourceTypes = [
    { value: 'pdf', label: 'PDF Document', icon: FileText },
    { value: 'url', label: 'Website Link', icon: LinkIcon },
    { value: 'document', label: 'Text Document', icon: FileText }
  ];

  useEffect(() => {
    fetchSources();
    fetchStats();
  }, []);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const response = await dataSourcesAPI.list();
      setSources(response.data);
    } catch (error) {
      console.error('Error fetching sources:', error);
      toast.error('Failed to load data sources');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await dataSourcesAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({ ...prev, file }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const formDataToSend = new FormData();
      
      // Add all fields to FormData
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== '') {
          if (key === 'file' && formData[key]) {
            formDataToSend.append(key, formData[key]);
          } else if (key !== 'file') {
            formDataToSend.append(key, formData[key]);
          }
        }
      });

      await dataSourcesAPI.create(formDataToSend);
      toast.success('Data source added successfully!');
      
      // Reset form and close dialog
      setFormData({
        title: '',
        description: '',
        source_type: 'url',
        category: 'reference',
        url: '',
        file: null,
        author: '',
        published_date: '',
        tags: '',
        summary: '',
        key_points: '',
        is_active: true
      });
      setIsAddDialogOpen(false);
      
      // Refresh list
      fetchSources();
      fetchStats();
    } catch (error) {
      console.error('Error adding source:', error);
      toast.error(error.response?.data?.error || 'Failed to add data source');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this data source?')) return;

    try {
      await dataSourcesAPI.delete(id);
      toast.success('Data source deleted');
      fetchSources();
      fetchStats();
    } catch (error) {
      console.error('Error deleting source:', error);
      toast.error('Failed to delete data source');
    }
  };

  const filteredSources = sources.filter(source => {
    const matchesSearch = source.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         source.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         source.tags?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = filterCategory === 'all' || source.category === filterCategory;
    const matchesType = filterType === 'all' || source.source_type === filterType;
    
    return matchesSearch && matchesCategory && matchesType;
  });

  const getCategoryBadgeColor = (category) => {
    const colors = {
      policy: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      research: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      data: 'bg-green-500/20 text-green-400 border-green-500/30',
      guideline: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      report: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      reference: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
      other: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    };
    return colors[category] || colors.other;
  };

  const getSourceIcon = (type) => {
    const icon = sourceTypes.find(t => t.value === type)?.icon;
    return icon || FileText;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white">Data Sources</h1>
          <p className="text-slate-400 mt-1">
            Manage PDFs and website links that the AI uses for reference
          </p>
        </div>
        
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Data Source
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-900 border-slate-800">
            <DialogHeader>
              <DialogTitle className="text-white">Add New Data Source</DialogTitle>
              <DialogDescription className="text-slate-400">
                Add a PDF document or website link for the AI to reference
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              {/* Title */}
              <div>
                <Label htmlFor="title" className="text-slate-300">Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  placeholder="e.g., Kenya National Allocation Policy 2024"
                  className="bg-slate-800 border-slate-700 text-white"
                  required
                />
              </div>

              {/* Source Type */}
              <div>
                <Label htmlFor="source_type" className="text-slate-300">Source Type *</Label>
                <Select value={formData.source_type} onValueChange={(value) => handleInputChange('source_type', value)}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {sourceTypes.map(type => (
                      <SelectItem key={type.value} value={type.value} className="text-white">
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* URL or File */}
              {formData.source_type === 'url' ? (
                <div>
                  <Label htmlFor="url" className="text-slate-300">Website URL *</Label>
                  <Input
                    id="url"
                    type="url"
                    value={formData.url}
                    onChange={(e) => handleInputChange('url', e.target.value)}
                    placeholder="https://example.com/document"
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>
              ) : (
                <div>
                  <Label htmlFor="file" className="text-slate-300">Upload File *</Label>
                  <Input
                    id="file"
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.txt"
                    className="bg-slate-800 border-slate-700 text-white"
                    required
                  />
                </div>
              )}

              {/* Category */}
              <div>
                <Label htmlFor="category" className="text-slate-300">Category *</Label>
                <Select value={formData.category} onValueChange={(value) => handleInputChange('category', value)}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-700">
                    {categories.map(cat => (
                      <SelectItem key={cat.value} value={cat.value} className="text-white">
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Description */}
              <div>
                <Label htmlFor="description" className="text-slate-300">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Brief description of the content..."
                  className="bg-slate-800 border-slate-700 text-white"
                  rows={3}
                />
              </div>

              {/* Author */}
              <div>
                <Label htmlFor="author" className="text-slate-300">Author/Organization</Label>
                <Input
                  id="author"
                  value={formData.author}
                  onChange={(e) => handleInputChange('author', e.target.value)}
                  placeholder="e.g., Ministry of Planning"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              {/* Tags */}
              <div>
                <Label htmlFor="tags" className="text-slate-300">Tags (comma-separated)</Label>
                <Input
                  id="tags"
                  value={formData.tags}
                  onChange={(e) => handleInputChange('tags', e.target.value)}
                  placeholder="e.g., poverty, allocation, kenya"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              {/* Summary */}
              <div>
                <Label htmlFor="summary" className="text-slate-300">Summary</Label>
                <Textarea
                  id="summary"
                  value={formData.summary}
                  onChange={(e) => handleInputChange('summary', e.target.value)}
                  placeholder="Key points and summary (helps AI find relevant content)..."
                  className="bg-slate-800 border-slate-700 text-white"
                  rows={4}
                />
              </div>

              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                  Add Source
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Total Sources</p>
                  <p className="text-2xl font-bold text-white">{stats.total}</p>
                </div>
                <FileText className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Active</p>
                  <p className="text-2xl font-bold text-green-400">{stats.active}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">PDFs</p>
                  <p className="text-2xl font-bold text-purple-400">{stats.by_type?.pdf || 0}</p>
                </div>
                <FileText className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Websites</p>
                  <p className="text-2xl font-bold text-orange-400">{stats.by_type?.url || 0}</p>
                </div>
                <LinkIcon className="h-8 w-8 text-orange-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search sources..."
                  className="pl-10 bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>
            
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-full md:w-48 bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all" className="text-white">All Categories</SelectItem>
                {categories.map(cat => (
                  <SelectItem key={cat.value} value={cat.value} className="text-white">
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-full md:w-48 bg-slate-800 border-slate-700 text-white">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all" className="text-white">All Types</SelectItem>
                {sourceTypes.map(type => (
                  <SelectItem key={type.value} value={type.value} className="text-white">
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Sources List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {loading ? (
          <p className="text-slate-400 col-span-2 text-center py-8">Loading sources...</p>
        ) : filteredSources.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800 col-span-2">
            <CardContent className="p-8 text-center">
              <FileText className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No data sources found</p>
              <p className="text-sm text-slate-500 mt-2">Add your first PDF or website link</p>
            </CardContent>
          </Card>
        ) : (
          filteredSources.map((source) => {
            const SourceIcon = getSourceIcon(source.source_type);
            return (
              <motion.div
                key={source.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
                          <SourceIcon className="h-5 w-5 text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-white text-lg mb-2 truncate">
                            {source.title}
                          </CardTitle>
                          <div className="flex flex-wrap gap-2">
                            <Badge className={getCategoryBadgeColor(source.category)}>
                              {source.category}
                            </Badge>
                            {source.is_active && (
                              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                Active
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {source.source_location && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-slate-400 hover:text-white"
                            onClick={() => window.open(source.source_location, '_blank')}
                            title="Open source"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-red-400 hover:text-red-300"
                          onClick={() => handleDelete(source.id)}
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    {source.description && (
                      <p className="text-sm text-slate-400 mb-3">
                        {source.description}
                      </p>
                    )}
                    
                    <div className="space-y-2 text-xs text-slate-500">
                      {source.author && (
                        <div className="flex items-center gap-2">
                          <User className="h-3 w-3" />
                          <span>{source.author}</span>
                        </div>
                      )}
                      {source.tags && (
                        <div className="flex items-center gap-2">
                          <Tag className="h-3 w-3" />
                          <span>{source.tags}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-3 w-3" />
                        <span>Used {source.usage_count} times</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-3 w-3" />
                        <span>Added {new Date(source.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default DataSources;
