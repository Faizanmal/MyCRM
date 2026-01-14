// Advanced Search Component
/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { useState } from 'react';
import { Search, Save, Star, X, Plus } from 'lucide-react';
import axios from 'axios';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';


interface SearchFilter {
  field: string;
  operator: string;
  value: any;
}

interface SavedSearch {
  id: string;
  name: string;
  model_name: string;
  filters: Record<string, any>;
  is_shared: boolean;
}

export default function AdvancedSearch() {
  const [modelName, setModelName] = useState('contact_management.Contact');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilter[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [savedSearches] = useState<SavedSearch[]>([]);
  const { toast } = useToast();

  const MODELS = [
    { value: 'contact_management.Contact', label: 'Contacts', fields: ['name', 'email', 'phone', 'company'] },
    { value: 'lead_management.Lead', label: 'Leads', fields: ['name', 'email', 'source', 'status'] },
    { value: 'opportunity_management.Opportunity', label: 'Opportunities', fields: ['name', 'value', 'stage'] },
  ];

  const OPERATORS = [
    { value: 'exact', label: 'Equals' },
    { value: 'contains', label: 'Contains' },
    { value: 'startswith', label: 'Starts with' },
    { value: 'gt', label: 'Greater than' },
    { value: 'lt', label: 'Less than' },
    { value: 'in', label: 'In list' },
  ];

  const currentModel = MODELS.find(m => m.value === modelName);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const filtersObject: Record<string, any> = {};
      filters.forEach(f => {
        filtersObject[f.field] = { operator: f.operator, value: f.value };
      });

      const response = await axios.post('/api/core/search/', {
        model_name: modelName,
        query: searchQuery,
        filters: filtersObject,
        full_text_fields: currentModel?.fields,
        limit: 50,
      });

      setResults(response.data.results || response.data);
      toast({
        title: 'Search Complete',
        description: `Found ${response.data.results?.length || 0} results`,
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Search failed',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const addFilter = () => {
    setFilters([...filters, { field: currentModel?.fields[0] || '', operator: 'exact', value: '' }]);
  };

  const removeFilter = (index: number) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const updateFilter = (index: number, key: keyof SearchFilter, value: any) => {
    const newFilters = [...filters];
    newFilters[index] = { ...newFilters[index], [key]: value };
    setFilters(newFilters);
  };

  const saveSearch = async (name: string) => {
    try {
      const filtersObject: Record<string, any> = {};
      filters.forEach(f => {
        filtersObject[f.field] = { operator: f.operator, value: f.value };
      });

      await axios.post('/api/core/saved-searches/', {
        name,
        model_name: modelName,
        filters: filtersObject,
        is_shared: false,
      });

      toast({
        title: 'Success',
        description: 'Search saved successfully',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to save search',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Search className="h-8 w-8" />
            Advanced Search
          </h1>
          <p className="text-muted-foreground mt-1">Search across your CRM data with powerful filters</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Search Panel */}
        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Search Query</CardTitle>
              <CardDescription>Enter search terms and add filters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Model Selection */}
              <div>
                <Label>Search In</Label>
                <Select value={modelName} onValueChange={setModelName}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MODELS.map(model => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Search Input */}
              <div>
                <Label>Search Terms</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter search terms..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <Button onClick={handleSearch} disabled={loading}>
                    <Search className="h-4 w-4 mr-2" />
                    {loading ? 'Searching...' : 'Search'}
                  </Button>
                </div>
              </div>

              {/* Filters */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <Label>Filters</Label>
                  <Button onClick={addFilter} size="sm" variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Filter
                  </Button>
                </div>

                {filters.map((filter, index) => (
                  <div key={index} className="flex gap-2 items-end">
                    <div className="flex-1">
                      <Select
                        value={filter.field}
                        onValueChange={(value) => updateFilter(index, 'field', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Field" />
                        </SelectTrigger>
                        <SelectContent>
                          {currentModel?.fields.map(field => (
                            <SelectItem key={field} value={field}>
                              {field}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex-1">
                      <Select
                        value={filter.operator}
                        onValueChange={(value) => updateFilter(index, 'operator', value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Operator" />
                        </SelectTrigger>
                        <SelectContent>
                          {OPERATORS.map(op => (
                            <SelectItem key={op.value} value={op.value}>
                              {op.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex-1">
                      <Input
                        placeholder="Value"
                        value={filter.value}
                        onChange={(e) => updateFilter(index, 'value', e.target.value)}
                      />
                    </div>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFilter(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <SaveSearchDialog onSave={saveSearch} />
                <Button variant="outline" onClick={() => { setFilters([]); setSearchQuery(''); }}>
                  Clear All
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <Card>
            <CardHeader>
              <CardTitle>Search Results</CardTitle>
              <CardDescription>
                {results.length > 0 ? `${results.length} results found` : 'No results yet'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {results.length > 0 ? (
                <div className="space-y-2">
                  {results.slice(0, 20).map((result, index) => (
                    <Card key={index} className="p-4">
                      <div className="space-y-1">
                        <p className="font-medium">{result.name || result.title || 'Untitled'}</p>
                        <div className="flex gap-2 flex-wrap">
                          {Object.entries(result).slice(0, 4).map(([key, value]) => (
                            <Badge key={key} variant="outline" className="text-xs">
                              {key}: {String(value)}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Enter search terms and click Search to see results</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Saved Searches Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Saved Searches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {savedSearches.length > 0 ? (
                  savedSearches.map(search => (
                    <Button
                      key={search.id}
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {
                        setModelName(search.model_name);
                        // Load filters from saved search
                      }}
                    >
                      {search.name}
                    </Button>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No saved searches yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Save Search Dialog
function SaveSearchDialog({ onSave }: { onSave: (name: string) => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');

  const handleSave = () => {
    if (name.trim()) {
      onSave(name);
      setName('');
      setOpen(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Save className="h-4 w-4 mr-2" />
          Save Search
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save Search</DialogTitle>
          <DialogDescription>Save this search for quick access later</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="search-name">Search Name</Label>
            <Input
              id="search-name"
              placeholder="e.g., High-value Contacts"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

