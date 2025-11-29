class ApiConstants {
  // Base URL - Change this to your backend URL
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api';
  
  // Auth endpoints
  static const String login = '$apiVersion/auth/login/';
  static const String register = '$apiVersion/auth/register/';
  static const String logout = '$apiVersion/auth/logout/';
  static const String refreshToken = '$apiVersion/auth/refresh/';
  static const String userProfile = '$apiVersion/auth/user/';
  
  // Contacts endpoints
  static const String contacts = '$apiVersion/contacts/';
  static String contactDetail(int id) => '$apiVersion/contacts/$id/';
  
  // Leads endpoints
  static const String leads = '$apiVersion/leads/';
  static String leadDetail(int id) => '$apiVersion/leads/$id/';
  
  // Opportunities endpoints
  static const String opportunities = '$apiVersion/opportunities/';
  static String opportunityDetail(int id) => '$apiVersion/opportunities/$id/';
  
  // Tasks endpoints
  static const String tasks = '$apiVersion/tasks/';
  static String taskDetail(int id) => '$apiVersion/tasks/$id/';
  
  // Communications endpoints
  static const String communications = '$apiVersion/communications/';
  static String communicationDetail(int id) => '$apiVersion/communications/$id/';
  
  // Dashboard endpoints
  static const String dashboardStats = '$apiVersion/dashboard/stats/';
  static const String dashboardCharts = '$apiVersion/dashboard/charts/';
  
  // Reports endpoints
  static const String reports = '$apiVersion/reports/';
  static const String analytics = '$apiVersion/analytics/';
  
  // Campaign endpoints
  static const String campaigns = '$apiVersion/campaigns/';
  
  // Documents endpoints
  static const String documents = '$apiVersion/documents/';
  
  // Integration endpoints
  static const String integrations = '$apiVersion/integrations/';
  
  // AI Insights endpoints
  static const String aiInsights = '$apiVersion/ai-insights/';
  
  // Gamification endpoints
  static const String gamification = '$apiVersion/gamification/';
}
