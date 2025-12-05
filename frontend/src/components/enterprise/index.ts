// Enterprise Components Index
// Export all enterprise feature components

// Existing components
export { default as PermissionManagement } from './PermissionManagement';
export { default as WorkflowBuilder } from './WorkflowBuilder';
export { default as DataImportExport } from './DataImportExport';
export { default as AdvancedSearch } from './AdvancedSearch';
export { default as EmailCampaignManager } from './EmailCampaignManager';
export { DashboardBuilder, ReportBuilder } from './DashboardAndReports';
export { default as LeadScoringDashboard } from './LeadScoringDashboard';
export { default as AuditLogViewer } from './AuditLogViewer';
export { default as NotificationCenter } from './NotificationCenter';
export { default as SecurityDashboard } from './SecurityDashboard';
export { default as WorkflowAutomation } from './WorkflowAutomation';
export { default as AIAnalyticsDashboard } from './AIAnalyticsDashboard';

// New enterprise components
export { HealthDashboard } from './HealthDashboard';
export { AIAssistantChat } from './AIAssistantChat';
export { ComplianceDashboard } from './ComplianceDashboard';
export { AnalyticsDashboard } from './AnalyticsDashboard';
export {
  RealtimeProvider,
  useRealtime,
  useChannel,
  usePresence,
  useConnectionStatus,
  useCollaborativeEditing,
  useLiveActivityFeed,
  ConnectionIndicator,
} from './RealtimeProvider';
