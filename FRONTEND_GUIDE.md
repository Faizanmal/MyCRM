# Frontend Implementation Guide

## 🎨 New Frontend Features Implementation

This document outlines all the frontend components created for the new enterprise features.

---

## 📦 Updated API Client (`src/lib/api.ts`)

### New API Modules Added:

#### 1. **Campaign Management API** (`campaignAPI`)
```typescript
- getCampaigns() - List all campaigns
- getCampaign(id) - Get campaign details
- createCampaign(data) - Create new campaign
- scheduleCampaign(id, scheduledAt) - Schedule campaign
- sendCampaignNow(id) - Send campaign immediately
- getCampaignAnalytics(id) - Get campaign performance
- getCampaignStatistics() - Get overall statistics
- getSegments() - List segments
- getTemplates() - List email templates
```

#### 2. **Pipeline Analytics API** (`analyticsAPI`)
```typescript
- getPipelineAnalytics() - Get pipeline health metrics
- getSalesForecast(months) - Get sales forecasts
- getAIInsights() - Get AI-powered insights
```

#### 3. **Document Management API** (`documentAPI`)
```typescript
- getDocuments(params) - List documents with filters
- uploadDocument(formData) - Upload new document
- downloadDocument(id) - Download document file
- createDocumentVersion(id, file) - Create new version
- shareDocument(id, data) - Share with team members
- requestApproval(id, approverId) - Request approval
- approveDocument(id, comments) - Approve document
- rejectDocument(id, comments) - Reject document
```

#### 4. **Integration Hub API** (`integrationAPI`)
```typescript
- getWebhooks() - List webhooks
- createWebhook(data) - Create new webhook
- testWebhook(id) - Send test webhook
- activateWebhook(id) - Enable webhook
- getIntegrations() - List integrations
- syncIntegration(id) - Trigger sync
- testIntegration(id) - Test connection
```

#### 5. **Activity Feed API** (`activityAPI`)
```typescript
- getActivities(params) - Get activity stream
- getMyFeed() - Get personalized feed
- getEntityActivities(model, id) - Get entity-specific activities
- getComments(model, id) - Get comments for entity
- addComment(data) - Post new comment
- getNotifications() - Get user notifications
- markNotificationRead(id) - Mark as read
- followEntity(model, id) - Follow entity
```

---

## 📄 New Pages Created

### 1. **Documents Page** (`/app/documents/page.tsx`)

**Features:**
- ✅ Document grid view with icons based on file type
- ✅ Upload multiple documents with drag & drop support
- ✅ Real-time search and filtering by document type
- ✅ Document preview cards with version info
- ✅ Download and share actions
- ✅ Approval status badges
- ✅ Responsive grid layout (1-4 columns)

**Components Used:**
- Upload button with file input
- Search bar with icon
- Filter dropdown (Contracts, Proposals, Invoices, etc.)
- Document cards with metadata
- Status badges (approved, pending, rejected)

**Endpoints:**
- GET `/api/documents/documents/`
- POST `/api/documents/documents/` (upload)
- GET `/api/documents/documents/{id}/download/`

---

### 2. **Pipeline Analytics Page** (`/app/analytics/pipeline/page.tsx`)

**Features:**
- ✅ Real-time pipeline health score (0-100)
- ✅ Key metrics dashboard (4 cards)
- ✅ Sales forecast chart (3/6/12 months)
- ✅ Conversion funnel visualization
- ✅ Pipeline by stage pie chart
- ✅ Deal velocity by stage bar chart
- ✅ AI-powered insights panel
- ✅ Confidence intervals on forecasts

**Charts Library:** `recharts`
- LineChart for sales forecast
- BarChart for conversion funnel & velocity
- PieChart for pipeline distribution

**Metrics Displayed:**
1. Pipeline Health Score with progress bar
2. Total Pipeline Value ($)
3. Average Deal Velocity (days)
4. Overall Conversion Rate (%)

**AI Insights:**
- Priority-based color coding (red/yellow/blue)
- Actionable recommendations
- Real-time analysis

**Endpoints:**
- GET `/api/core/analytics/pipeline_analytics/`
- GET `/api/core/analytics/sales_forecast/?months=3`
- GET `/api/core/analytics/ai_insights_dashboard/`

---

### 3. **Integrations Page** (`/app/integrations/page.tsx`)

**Features:**
- ✅ Two-tab interface (Integrations | Webhooks)
- ✅ Integration cards with platform icons
- ✅ Status indicators (connected, error, syncing)
- ✅ Test and Sync actions
- ✅ Webhooks table with event badges
- ✅ Enable/Disable webhooks
- ✅ Last sync/delivery timestamps

**Integrations Tab:**
- Grid of integration cards (3 columns)
- Platform logos (Slack, Teams, Salesforce, etc.)
- Connection status with animated icons
- Test and Sync Now buttons
- Auth type display

**Webhooks Tab:**
- Full-width table view
- Event badges (multiple events per webhook)
- URL display with truncation
- Active/Inactive status toggle
- Test webhook functionality
- Last delivery timestamp

**Endpoints:**
- GET `/api/integrations/integrations/`
- POST `/api/integrations/integrations/{id}/test/`
- POST `/api/integrations/integrations/{id}/sync/`
- GET `/api/integrations/webhooks/`
- POST `/api/integrations/webhooks/{id}/test/`
- POST `/api/integrations/webhooks/{id}/activate/`

---

## 🧩 New Reusable Components

### 1. **ActivityFeed Component** (`/components/ActivityFeed.tsx`)

**Props:**
```typescript
interface ActivityFeedProps {
  entityModel?: string;      // e.g., 'lead', 'contact', 'opportunity'
  entityId?: string;          // Entity ID to filter activities
  showComments?: boolean;     // Show comments tab
  maxHeight?: string;         // Max height for scrolling
}
```

**Features:**
- ✅ Two-tab interface (Activity | Comments)
- ✅ Activity stream with type-based icons
- ✅ Comment posting with @mention support
- ✅ Real-time "time ago" formatting
- ✅ Reply count display
- ✅ Scroll container with max height
- ✅ Empty states for both tabs

**Usage Example:**
```tsx
// Show all user activities
<ActivityFeed />

// Show activities for specific lead
<ActivityFeed 
  entityModel="lead" 
  entityId="123" 
  showComments={true}
  maxHeight="500px"
/>
```

**Activity Types:**
- comment (blue chat icon)
- mention (purple @ icon)
- status_change (green bell)
- assignment (orange user icon)

---

### 2. **NotificationsDropdown Component** (`/components/NotificationsDropdown.tsx`)

**Features:**
- ✅ Bell icon with unread count badge
- ✅ Dropdown panel (positioned right)
- ✅ Real-time polling (every 30 seconds)
- ✅ Mark individual notifications as read
- ✅ Mark all as read action
- ✅ Unread notifications highlighted (blue background)
- ✅ Click-outside to close
- ✅ Time ago formatting
- ✅ Scroll container for long lists

**Visual Design:**
- Badge shows count (max 99+)
- Unread notifications have blue-50 background
- Read notifications fade to gray
- Check icon to mark as read
- Empty state with illustration

**Usage:**
```tsx
// Add to header/navbar
import NotificationsDropdown from '@/components/NotificationsDropdown';

<NotificationsDropdown />
```

**Auto-refresh:**
- Polls every 30 seconds for new notifications
- Updates badge count in real-time
- Loads full list when dropdown opens

---

## 🎨 Design System

### Color Palette
- **Primary Blue:** `#3B82F6` (buttons, links, charts)
- **Success Green:** `#10B981` (approvals, health)
- **Warning Yellow:** `#F59E0B` (pending, medium priority)
- **Danger Red:** `#EF4444` (errors, high priority)
- **Purple:** `#8B5CF6` (mentions, special features)
- **Orange:** `#EC4899` (assignments, alerts)

### Status Colors
```tsx
// Campaigns
draft: 'bg-gray-100 text-gray-800'
scheduled: 'bg-blue-100 text-blue-800'
sent: 'bg-green-100 text-green-800'
paused: 'bg-yellow-100 text-yellow-800'

// Documents
approved: 'text-green-600 bg-green-50'
pending: 'text-yellow-600 bg-yellow-50'
rejected: 'text-red-600 bg-red-50'

// Integrations
connected: 'text-green-600 bg-green-50'
error: 'text-red-600 bg-red-50'
syncing: 'text-blue-600 bg-blue-50'
```

### Icons (Heroicons)
- **Documents:** `DocumentIcon`, `FolderIcon`, `CloudArrowUpIcon`
- **Analytics:** `ChartBarIcon`, `ArrowTrendingUpIcon`
- **Activity:** `BellIcon`, `ChatBubbleLeftIcon`, `AtSymbolIcon`
- **Integrations:** `PuzzlePieceIcon`, `BoltIcon`, `LinkIcon`

---

## 📊 Charts & Visualizations

### Recharts Components Used:

#### 1. **Line Chart** (Sales Forecast)
```tsx
<LineChart data={forecast?.monthly_forecast}>
  <Line dataKey="predicted_revenue" stroke="#3B82F6" />
  <Line dataKey="confidence_lower" strokeDasharray="5 5" />
  <Line dataKey="confidence_upper" strokeDasharray="5 5" />
</LineChart>
```

#### 2. **Bar Chart** (Conversion Funnel, Deal Velocity)
```tsx
<BarChart data={analytics?.conversion_funnel?.stage_metrics}>
  <Bar dataKey="count" fill="#3B82F6" name="Opportunities" />
  <Bar dataKey="value" fill="#10B981" name="Value ($)" />
</BarChart>
```

#### 3. **Pie Chart** (Pipeline by Stage)
```tsx
<PieChart>
  <Pie 
    data={analytics?.pipeline_health?.by_stage}
    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
  />
</PieChart>
```

**Chart Configuration:**
- Responsive container (100% width)
- Tooltips with currency formatting
- Grid lines with `strokeDasharray="3 3"`
- Legends with custom names
- Custom colors from palette

---

## 🔧 Integration with Existing Components

### MainLayout
All new pages use the existing `MainLayout` wrapper:
```tsx
<ProtectedRoute>
  <MainLayout>
    {/* Page content */}
  </MainLayout>
</ProtectedRoute>
```

### ProtectedRoute
Authentication guard applied to all pages

### Existing UI Components
- `Card`, `CardContent` (used in campaigns)
- Standard Tailwind classes for consistency

---

## 📱 Responsive Design

All pages implement responsive breakpoints:

```css
/* Grid Columns */
grid-cols-1           /* Mobile */
md:grid-cols-2        /* Tablet */
lg:grid-cols-3        /* Desktop */
xl:grid-cols-4        /* Large Desktop */

/* Flex Direction */
flex-col              /* Mobile */
sm:flex-row           /* Tablet+ */

/* Padding/Spacing */
p-4 lg:p-6           /* Adaptive padding */
gap-4 lg:gap-6       /* Adaptive gaps */
```

**Mobile-First Approach:**
- Stack cards vertically on mobile
- Hide secondary actions in dropdowns
- Reduce chart heights
- Simplify tables to cards

---

## 🚀 Next Steps

### 1. **Add to Navigation**
Update the main navigation to include new pages:
```tsx
// src/components/Layout/Sidebar.tsx or similar
const menuItems = [
  // ... existing items
  { 
    name: 'Campaigns', 
    href: '/campaigns', 
    icon: EnvelopeIcon 
  },
  { 
    name: 'Documents', 
    href: '/documents', 
    icon: DocumentIcon 
  },
  { 
    name: 'Pipeline Analytics', 
    href: '/analytics/pipeline', 
    icon: ChartBarIcon 
  },
  { 
    name: 'Integrations', 
    href: '/integrations', 
    icon: PuzzlePieceIcon 
  },
];
```

### 2. **Add Notifications to Header**
```tsx
// In your header component
import NotificationsDropdown from '@/components/NotificationsDropdown';

<NotificationsDropdown />
```

### 3. **Add Activity Feed to Entity Pages**
```tsx
// In Lead/Contact/Opportunity detail pages
import ActivityFeed from '@/components/ActivityFeed';

<ActivityFeed 
  entityModel="lead" 
  entityId={leadId} 
  showComments={true}
/>
```

### 4. **Install Required Packages**
```bash
cd frontend
npm install recharts
```

### 5. **Environment Variables**
Ensure `.env.local` has:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 🧪 Testing Checklist

### Documents Page
- [ ] Upload single and multiple files
- [ ] Download documents
- [ ] Search and filter by type
- [ ] Responsive grid (1-4 columns)
- [ ] Empty state displays correctly

### Analytics Page
- [ ] All 4 metric cards load
- [ ] Forecast chart renders with data
- [ ] Change forecast period (3/6/12 months)
- [ ] Pie chart shows stage distribution
- [ ] AI insights display (or empty state)
- [ ] Charts are responsive

### Integrations Page
- [ ] Switch between tabs
- [ ] Test integration connection
- [ ] Sync integration
- [ ] Enable/disable webhooks
- [ ] Test webhook delivery
- [ ] Empty states for both tabs

### Activity Feed
- [ ] Load activities for entity
- [ ] Post comments with @mentions
- [ ] Switch between Activity/Comments tabs
- [ ] Scroll long lists
- [ ] Time ago updates correctly

### Notifications
- [ ] Badge shows unread count
- [ ] Dropdown opens/closes
- [ ] Mark individual as read
- [ ] Mark all as read
- [ ] Polling updates count
- [ ] Click outside closes

---

## 📚 API Response Examples

### Campaign Statistics
```json
{
  "total_campaigns": 25,
  "avg_open_rate": 24.5,
  "avg_click_rate": 3.2,
  "total_sent": 15234
}
```

### Pipeline Analytics
```json
{
  "pipeline_health": {
    "health_score": 78,
    "total_pipeline_value": 1234567,
    "deal_count": 45,
    "by_stage": [
      { "stage": "Qualification", "value": 250000, "count": 12 },
      { "stage": "Proposal", "value": 450000, "count": 8 }
    ]
  },
  "conversion_funnel": {
    "overall_conversion_rate": 28.5,
    "stage_metrics": [...]
  },
  "deal_velocity": {
    "average_days": 32,
    "by_stage": [...]
  }
}
```

### Document List
```json
{
  "results": [
    {
      "id": "123",
      "title": "Contract-2024.pdf",
      "document_type": "contract",
      "mime_type": "application/pdf",
      "version": 2,
      "approval_status": "approved",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

## 🎯 Feature Highlights

### 🚀 Campaign Management
- Full CRUD operations
- Schedule campaigns for future dates
- Real-time analytics (opens, clicks)
- A/B testing support
- Email templates library

### 📊 Pipeline Analytics
- AI-powered health scoring
- 3/6/12 month forecasting
- Conversion funnel analysis
- Deal velocity tracking
- Actionable insights

### 📁 Document Management
- Version control system
- OCR text extraction (backend)
- Secure sharing
- Approval workflows
- Comment threads

### 🔌 Integration Hub
- Webhook management
- OAuth integrations
- Sync with external platforms
- Delivery logs
- Test functionality

### 📢 Activity Feed
- Real-time updates
- @mention support
- Comment threading
- Follow entities
- Smart notifications

---

## 💡 Tips & Best Practices

1. **Error Handling:** All API calls wrapped in try-catch
2. **Loading States:** Spinners displayed during data fetch
3. **Empty States:** Helpful messages when no data
4. **Responsive Design:** Mobile-first approach
5. **Accessibility:** Semantic HTML and ARIA labels
6. **Performance:** Lazy loading for heavy components
7. **Code Reusability:** Shared components for common patterns

---

## 📞 Support

For questions or issues:
1. Check backend API documentation in `FEATURES.md`
2. Review Django admin for data verification
3. Check browser console for API errors
4. Verify environment variables are set

---

**Status:** ✅ **All Frontend Components Complete**

**Last Updated:** 2024
**Version:** 1.0.0
