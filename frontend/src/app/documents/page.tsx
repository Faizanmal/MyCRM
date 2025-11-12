'use client';

import { useState, useEffect, useCallback } from 'react';
import { documentAPI } from '@/lib/api';
import MainLayout from '@/components/Layout/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
  FolderIcon,
  CloudArrowUpIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EllipsisVerticalIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface Document {
  id: string;
  name?: string;
  title?: string;
  file?: string;
  uploaded_at?: string;
  created_at?: string;
  size?: number;
  type?: string;
  mime_type?: string;
  status?: string;
  version?: number;
  description?: string;
  approval_status?: string;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [uploading, setUploading] = useState(false);

  const loadDocuments = useCallback(async () => {
    try {
      const params = filterType !== 'all' ? { document_type: filterType } : {};
      const response = await documentAPI.getDocuments(params);
      setDocuments(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  }, [filterType]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i]);
        formData.append('title', files[i].name);
        formData.append('document_type', 'general');
        
        await documentAPI.uploadDocument(formData);
      }
      await loadDocuments();
    } catch (error) {
      console.error('Failed to upload files:', error);
      alert('Failed to upload one or more files');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (document: Document) => {
    try {
      const response = await documentAPI.downloadDocument(document.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = window.document.createElement('a');
      link.href = url;
      link.setAttribute('download', (document.file || 'download').split('/').pop() || 'download');
      window.document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to download document:', error);
      alert('Failed to download document');
    }
  };

  const getDocumentIcon = (mimeType: string) => {
    if (mimeType?.includes('pdf')) return '📄';
    if (mimeType?.includes('image')) return '🖼️';
    if (mimeType?.includes('word') || mimeType?.includes('document')) return '📝';
    if (mimeType?.includes('sheet') || mimeType?.includes('excel')) return '📊';
    if (mimeType?.includes('presentation')) return '📽️';
    return '📎';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-50';
      case 'pending': return 'text-yellow-600 bg-yellow-50';
      case 'rejected': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const filteredDocuments = documents.filter(doc =>
    (doc.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (doc.description || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
              <p className="text-gray-600 mt-1">Manage your organization&apos;s documents</p>
            </div>
            <div className="flex items-center space-x-3">
              <label className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer">
                <CloudArrowUpIcon className="w-5 h-5 mr-2" />
                {uploading ? 'Uploading...' : 'Upload'}
                <input
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="bg-white rounded-lg shadow mb-6 p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-center space-x-2">
                <FunnelIcon className="w-5 h-5 text-gray-400" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Types</option>
                  <option value="contract">Contracts</option>
                  <option value="proposal">Proposals</option>
                  <option value="invoice">Invoices</option>
                  <option value="report">Reports</option>
                  <option value="presentation">Presentations</option>
                  <option value="general">General</option>
                </select>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* Documents Grid */}
              {filteredDocuments.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-12 text-center">
                  <FolderIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
                  <p className="text-gray-500">Upload your first document to get started</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {filteredDocuments.map((document) => (
                    <div
                      key={document.id}
                      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4"
                    >
                      {/* Document Icon */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="text-4xl">
                          {getDocumentIcon(document.mime_type || '')}
                        </div>
                        <div className="relative">
                          <button className="p-1 hover:bg-gray-100 rounded">
                            <EllipsisVerticalIcon className="w-5 h-5 text-gray-400" />
                          </button>
                        </div>
                      </div>

                      {/* Document Info */}
                      <h3 className="font-medium text-gray-900 mb-1 truncate" title={document.title}>
                        {document.title}
                      </h3>
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                        {document.description || 'No description'}
                      </p>

                      {/* Document Meta */}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                        <span>v{document.version || 1}</span>
                        <span>{document.created_at ? new Date(document.created_at).toLocaleDateString() : 'N/A'}</span>
                      </div>

                      {/* Status Badge */}
                      {document.approval_status && (
                        <div className="mb-3">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(document.approval_status)}`}>
                            {document.approval_status === 'approved' ? (
                              <CheckCircleIcon className="w-3 h-3 mr-1" />
                            ) : (
                              <ClockIcon className="w-3 h-3 mr-1" />
                            )}
                            {document.approval_status}
                          </span>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleDownload(document)}
                          className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 text-sm font-medium flex items-center justify-center"
                        >
                          <ArrowDownTrayIcon className="w-4 h-4 mr-1" />
                          Download
                        </button>
                        <button className="px-3 py-2 bg-gray-50 text-gray-600 rounded hover:bg-gray-100">
                          <ShareIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
