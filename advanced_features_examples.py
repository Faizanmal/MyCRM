"""
Advanced Features API Examples
Test scripts for all new features
"""
import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Authentication token (get from login)
TOKEN = "your-jwt-token-here"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


# ============================================================================
# 1. ADVANCED ANALYTICS
# ============================================================================

def test_sales_forecast():
    """Test sales forecasting"""
    print("\n=== Sales Forecast ===")
    response = requests.get(
        f"{API_V1}/analytics/forecast/",
        params={"periods": 30},
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_conversion_funnel():
    """Test conversion funnel analysis"""
    print("\n=== Conversion Funnel ===")
    response = requests.get(
        f"{API_V1}/analytics/funnel/",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_cohort_analysis():
    """Test cohort analysis"""
    print("\n=== Cohort Analysis ===")
    response = requests.get(
        f"{API_V1}/analytics/cohort/",
        params={
            "metric": "retention",
            "period": "month",
            "cohorts": 12
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_custom_metrics():
    """Test custom metrics"""
    print("\n=== Custom Metrics ===")
    response = requests.get(
        f"{API_V1}/analytics/metrics/",
        params={
            "metrics": "avg_deal_size,win_rate,sales_velocity",
            "group_by": "month"
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# 2. EMAIL CAMPAIGNS
# ============================================================================

def create_email_template():
    """Create an email template"""
    print("\n=== Create Email Template ===")
    data = {
        "name": "Welcome Email",
        "subject": "Welcome to {{company_name}}, {{first_name}}!",
        "body_html": """
            <html>
            <body>
                <h1>Welcome, {{first_name}}!</h1>
                <p>Thank you for joining {{company_name}}.</p>
                <p><a href="{{activation_link}}">Activate your account</a></p>
            </body>
            </html>
        """,
        "body_text": "Welcome {{first_name}}! Thank you for joining {{company_name}}.",
        "variables": ["first_name", "company_name", "activation_link"],
        "category": "onboarding"
    }
    response = requests.post(
        f"{API_V1}/email-templates/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def create_email_campaign(template_id):
    """Create an email campaign"""
    print("\n=== Create Email Campaign ===")
    data = {
        "name": "Q1 Product Launch",
        "template": template_id,
        "segment_filter": {"industry": "technology"},
        "scheduled_send": (datetime.now() + timedelta(days=1)).isoformat(),
        "from_email": "sales@company.com",
        "from_name": "Sales Team"
    }
    response = requests.post(
        f"{API_V1}/email-campaigns/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def send_campaign(campaign_id):
    """Send an email campaign"""
    print(f"\n=== Send Campaign {campaign_id} ===")
    response = requests.post(
        f"{API_V1}/email-campaigns/{campaign_id}/send/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def get_campaign_stats(campaign_id):
    """Get campaign statistics"""
    print(f"\n=== Campaign Stats {campaign_id} ===")
    response = requests.get(
        f"{API_V1}/email-campaigns/{campaign_id}/stats/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# 3. AUDIT TRAIL
# ============================================================================

def get_audit_trail():
    """Get audit trail"""
    print("\n=== Audit Trail ===")
    response = requests.get(
        f"{API_V1}/audit-trail/",
        params={
            "model": "lead",
            "start_date": "2024-01-01",
            "ordering": "-timestamp"
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total: {data.get('count')}")
    for entry in data.get("results", [])[:5]:
        print(f"  - {entry['timestamp']}: {entry['action']} by {entry['user_name']}")


def get_field_history():
    """Get field change history"""
    print("\n=== Field History ===")
    response = requests.get(
        f"{API_V1}/field-history/",
        params={
            "model": "opportunity",
            "object_id": 1,
            "field_name": "amount"
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def get_audit_stats():
    """Get audit statistics"""
    print("\n=== Audit Statistics ===")
    response = requests.get(
        f"{API_V1}/audit-trail/stats/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# 4. DASHBOARD WIDGETS
# ============================================================================

def create_widget():
    """Create a dashboard widget"""
    print("\n=== Create Widget ===")
    data = {
        "name": "Sales This Month",
        "widget_type": "metric_card",
        "data_source": "opportunities_value",
        "query_params": {"stage": "won", "this_month": True},
        "size": "medium",
        "color_scheme": "blue",
        "icon": "currency-dollar",
        "value_prefix": "$",
        "refresh_interval": 300
    }
    response = requests.post(
        f"{API_V1}/widgets/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def get_widget_data(widget_id):
    """Get widget data"""
    print(f"\n=== Widget Data {widget_id} ===")
    response = requests.get(
        f"{API_V1}/widgets/{widget_id}/data/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def create_dashboard():
    """Create a dashboard"""
    print("\n=== Create Dashboard ===")
    data = {
        "name": "Sales Dashboard",
        "description": "Key sales metrics and pipeline",
        "layout_config": {"columns": 12, "rowHeight": 100},
        "is_default": True
    }
    response = requests.post(
        f"{API_V1}/dashboards/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def add_widget_to_dashboard(dashboard_id, widget_id):
    """Add widget to dashboard"""
    print(f"\n=== Add Widget {widget_id} to Dashboard {dashboard_id} ===")
    data = {
        "widget_id": widget_id,
        "row": 0,
        "column": 0,
        "width": 6,
        "height": 2
    }
    response = requests.post(
        f"{API_V1}/dashboards/{dashboard_id}/add_widget/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# 5. CUSTOM FIELDS
# ============================================================================

def create_custom_field():
    """Create a custom field"""
    print("\n=== Create Custom Field ===")
    data = {
        "name": "annual_revenue",
        "label": "Annual Revenue",
        "field_type": "decimal",
        "content_type": 5,  # Lead content type ID
        "is_required": True,
        "min_value": 0,
        "max_value": 999999999,
        "help_text": "Company's annual revenue in USD",
        "placeholder": "e.g., 1000000",
        "is_searchable": True,
        "is_filterable": True
    }
    response = requests.post(
        f"{API_V1}/custom-fields/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def create_select_field():
    """Create a select field with options"""
    print("\n=== Create Select Field ===")
    data = {
        "name": "company_size",
        "label": "Company Size",
        "field_type": "select",
        "content_type": 5,  # Lead content type ID
        "options": [
            {"value": "1-10", "label": "1-10 employees"},
            {"value": "11-50", "label": "11-50 employees"},
            {"value": "51-200", "label": "51-200 employees"},
            {"value": "201+", "label": "201+ employees"}
        ],
        "is_required": False
    }
    response = requests.post(
        f"{API_V1}/custom-fields/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get("id")


def set_custom_field_values():
    """Set custom field values for an object"""
    print("\n=== Set Custom Field Values ===")
    data = {
        "model": "lead",
        "object_id": 1,
        "values": {
            "1": 2500000,  # annual_revenue field
            "2": "51-200"  # company_size field
        }
    }
    response = requests.post(
        f"{API_V1}/custom-field-values/bulk_update/",
        json=data,
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def get_custom_field_values():
    """Get custom field values for an object"""
    print("\n=== Get Custom Field Values ===")
    response = requests.get(
        f"{API_V1}/custom-field-values/for_object/",
        params={"model": "lead", "object_id": 1},
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================================================
# 6. ACTIVITY TIMELINE
# ============================================================================

def get_activity_timeline():
    """Get unified activity timeline"""
    print("\n=== Activity Timeline ===")
    response = requests.get(
        f"{API_V1}/timeline/",
        params={
            "start_date": "2024-01-01",
            "limit": 50
        },
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total: {data.get('count')}")
    for item in data.get("results", [])[:10]:
        print(f"  - {item['timestamp']}: {item['action']} on {item['entity_type']} by {item['user']['name']}")


def get_entity_timeline():
    """Get timeline for specific entity"""
    print("\n=== Entity Timeline (Lead #123) ===")
    response = requests.get(
        f"{API_V1}/timeline/lead/123/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def get_user_activity():
    """Get user activity timeline"""
    print("\n=== User Activity ===")
    response = requests.get(
        f"{API_V1}/timeline/user/",
        headers=HEADERS
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total activities: {data.get('count')}")
    for item in data.get("timeline", [])[:5]:
        print(f"  - {item['timestamp']}: {item['action']}")


# ============================================================================
# 7. WEBSOCKET NOTIFICATIONS (JavaScript)
# ============================================================================

websocket_example = """
// WebSocket Notification Example (JavaScript)

const socket = new WebSocket('ws://localhost:8000/ws/notifications/');

socket.onopen = () => {
    console.log('Connected to notifications');
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    if (data.type === 'notification') {
        // Display notification
        showNotification(data.notification);
    }
};

socket.onerror = (error) => {
    console.error('WebSocket error:', error);
};

socket.onclose = () => {
    console.log('Disconnected from notifications');
};

// Mark notification as read
function markAsRead(notificationId) {
    socket.send(JSON.stringify({
        type: 'mark_read',
        notification_id: notificationId
    }));
}

// Keep connection alive
setInterval(() => {
    socket.send(JSON.stringify({
        type: 'ping',
        timestamp: new Date().toISOString()
    }));
}, 30000);
"""


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all API tests"""
    print("=" * 80)
    print("ADVANCED FEATURES API TESTS")
    print("=" * 80)
    
    # Analytics
    print("\n" + "=" * 80)
    print("ANALYTICS TESTS")
    print("=" * 80)
    test_sales_forecast()
    test_conversion_funnel()
    test_cohort_analysis()
    test_custom_metrics()
    
    # Email Campaigns
    print("\n" + "=" * 80)
    print("EMAIL CAMPAIGN TESTS")
    print("=" * 80)
    template_id = create_email_template()
    if template_id:
        campaign_id = create_email_campaign(template_id)
        if campaign_id:
            get_campaign_stats(campaign_id)
    
    # Audit Trail
    print("\n" + "=" * 80)
    print("AUDIT TRAIL TESTS")
    print("=" * 80)
    get_audit_trail()
    get_field_history()
    get_audit_stats()
    
    # Dashboard Widgets
    print("\n" + "=" * 80)
    print("DASHBOARD WIDGET TESTS")
    print("=" * 80)
    widget_id = create_widget()
    dashboard_id = create_dashboard()
    if widget_id and dashboard_id:
        add_widget_to_dashboard(dashboard_id, widget_id)
        get_widget_data(widget_id)
    
    # Custom Fields
    print("\n" + "=" * 80)
    print("CUSTOM FIELD TESTS")
    print("=" * 80)
    create_custom_field()
    create_select_field()
    set_custom_field_values()
    get_custom_field_values()
    
    # Activity Timeline
    print("\n" + "=" * 80)
    print("ACTIVITY TIMELINE TESTS")
    print("=" * 80)
    get_activity_timeline()
    get_entity_timeline()
    get_user_activity()
    
    # WebSocket Example
    print("\n" + "=" * 80)
    print("WEBSOCKET EXAMPLE (JavaScript)")
    print("=" * 80)
    print(websocket_example)
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        if hasattr(sys.modules[__name__], test_name):
            globals()[test_name]()
        else:
            print(f"Test '{test_name}' not found")
    else:
        # Run all tests
        run_all_tests()


# ============================================================================
# CURL EXAMPLES
# ============================================================================

curl_examples = """
# CURL EXAMPLES FOR ADVANCED FEATURES

# Get sales forecast
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/analytics/forecast/?periods=30"

# Get conversion funnel
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/analytics/funnel/"

# Create email template
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Welcome","subject":"Hello {{name}}","body_text":"Welcome!"}' \\
  "http://localhost:8000/api/v1/email-templates/"

# Get audit trail
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/audit-trail/?model=lead&start_date=2024-01-01"

# Create widget
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Sales","widget_type":"metric_card","data_source":"opportunities_value"}' \\
  "http://localhost:8000/api/v1/widgets/"

# Get widget data
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/widgets/1/data/"

# Create custom field
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"name":"revenue","label":"Revenue","field_type":"decimal","content_type":5}' \\
  "http://localhost:8000/api/v1/custom-fields/"

# Get activity timeline
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/timeline/?limit=50"

# Get entity timeline
curl -H "Authorization: Bearer $TOKEN" \\
  "http://localhost:8000/api/v1/timeline/lead/123/"
"""

print("\n\n" + curl_examples)
