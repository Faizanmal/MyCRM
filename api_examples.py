"""
MyCRM API Usage Examples
Comprehensive examples for using the MyCRM REST API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Your authentication token
TOKEN = "your_jwt_token_here"

# Headers for authenticated requests
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


# ============================================
# 1. AUTHENTICATION
# ============================================

def get_auth_token(username, password):
    """Get JWT authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"username": username, "password": password}
    )
    data = response.json()
    return data.get("access"), data.get("refresh")


# ============================================
# 2. LEADS API
# ============================================

def create_lead():
    """Create a new lead"""
    lead_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "company_name": "Acme Corporation",
        "job_title": "VP of Sales",
        "lead_source": "website",
        "priority": "high",
        "estimated_value": 50000.00,
        "notes": "Interested in enterprise plan"
    }
    
    response = requests.post(
        f"{API_V1}/leads/",
        headers=HEADERS,
        json=lead_data
    )
    return response.json()


def list_leads(filters=None):
    """List leads with optional filters"""
    params = filters or {}
    # Example: {"status": "qualified", "priority": "high", "assigned_to_me": "true"}
    
    response = requests.get(
        f"{API_V1}/leads/",
        headers=HEADERS,
        params=params
    )
    return response.json()


def search_leads(query):
    """Search leads by name, email, or company"""
    response = requests.get(
        f"{API_V1}/leads/",
        headers=HEADERS,
        params={"search": query}
    )
    return response.json()


def get_lead(lead_id):
    """Get detailed lead information"""
    response = requests.get(
        f"{API_V1}/leads/{lead_id}/",
        headers=HEADERS
    )
    return response.json()


def update_lead(lead_id, updates):
    """Update a lead (PATCH)"""
    response = requests.patch(
        f"{API_V1}/leads/{lead_id}/",
        headers=HEADERS,
        json=updates
    )
    return response.json()


def convert_lead(lead_id):
    """Convert lead to contact and opportunity"""
    response = requests.post(
        f"{API_V1}/leads/{lead_id}/convert/",
        headers=HEADERS
    )
    return response.json()


def get_lead_statistics():
    """Get lead statistics"""
    response = requests.get(
        f"{API_V1}/leads/statistics/",
        headers=HEADERS
    )
    return response.json()


def bulk_update_leads(lead_ids, action, data=None):
    """Bulk update or delete leads"""
    payload = {
        "ids": lead_ids,
        "action": action,  # "update" or "delete"
        "data": data or {}
    }
    
    response = requests.post(
        f"{API_V1}/leads/bulk_update/",
        headers=HEADERS,
        json=payload
    )
    return response.json()


# ============================================
# 3. CONTACTS API
# ============================================

def create_contact():
    """Create a new contact"""
    contact_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567891",
        "mobile": "+1234567892",
        "company_name": "Tech Innovations Inc",
        "job_title": "CTO",
        "contact_type": "customer",
        "address_line_1": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "country": "USA"
    }
    
    response = requests.post(
        f"{API_V1}/contacts/",
        headers=HEADERS,
        json=contact_data
    )
    return response.json()


def list_contacts(filters=None):
    """List contacts with optional filters"""
    params = filters or {}
    
    response = requests.get(
        f"{API_V1}/contacts/",
        headers=HEADERS,
        params=params
    )
    return response.json()


# ============================================
# 4. OPPORTUNITIES API
# ============================================

def create_opportunity(contact_id):
    """Create a new opportunity"""
    from datetime import datetime, timedelta
    
    opp_data = {
        "name": "Enterprise Software Deal",
        "description": "Annual subscription for 100 users",
        "company_name": "Tech Corp",
        "contact": contact_id,
        "stage": "proposal",
        "amount": 120000.00,
        "currency": "USD",
        "probability": 75,
        "expected_close_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    }
    
    response = requests.post(
        f"{API_V1}/opportunities/",
        headers=HEADERS,
        json=opp_data
    )
    return response.json()


def get_pipeline_statistics():
    """Get opportunity pipeline statistics"""
    response = requests.get(
        f"{API_V1}/opportunities/pipeline/",
        headers=HEADERS
    )
    return response.json()


# ============================================
# 5. TASKS API
# ============================================

def create_task(assigned_to_user_id):
    """Create a new task"""
    from datetime import datetime, timedelta
    
    task_data = {
        "title": "Follow up with prospect",
        "description": "Call to discuss pricing and timeline",
        "task_type": "call",
        "priority": "high",
        "status": "pending",
        "assigned_to": assigned_to_user_id,
        "due_date": (datetime.now() + timedelta(days=2)).isoformat()
    }
    
    response = requests.post(
        f"{API_V1}/tasks/",
        headers=HEADERS,
        json=task_data
    )
    return response.json()


def complete_task(task_id):
    """Mark a task as completed"""
    response = requests.post(
        f"{API_V1}/tasks/{task_id}/complete/",
        headers=HEADERS
    )
    return response.json()


def get_my_tasks():
    """Get tasks assigned to me"""
    response = requests.get(
        f"{API_V1}/tasks/",
        headers=HEADERS,
        params={"assigned_to_me": "true"}
    )
    return response.json()


def get_overdue_tasks():
    """Get overdue tasks"""
    response = requests.get(
        f"{API_V1}/tasks/",
        headers=HEADERS,
        params={"overdue": "true"}
    )
    return response.json()


# ============================================
# 6. CSV IMPORT/EXPORT
# ============================================

def import_leads_from_csv(csv_file_path):
    """Import leads from CSV file"""
    # Field mapping: CSV column name -> model field name
    mapping = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "Email": "email",
        "Phone": "phone",
        "Company": "company_name",
        "Job Title": "job_title",
        "Source": "lead_source"
    }
    
    with open(csv_file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'mapping': json.dumps(mapping),
            'update_existing': 'false',
            'skip_errors': 'true'
        }
        
        response = requests.post(
            f"{API_V1}/import/leads/",
            headers={"Authorization": f"Bearer {TOKEN}"},  # Don't set Content-Type for multipart
            files=files,
            data=data
        )
    
    return response.json()


def export_leads_to_csv(filters=None, output_file="leads_export.csv"):
    """Export leads to CSV file"""
    params = filters or {}
    
    response = requests.get(
        f"{API_V1}/export/leads/",
        headers=HEADERS,
        params=params,
        stream=True
    )
    
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_file


def download_import_template(resource_type, output_file=None):
    """Download CSV import template"""
    if not output_file:
        output_file = f"{resource_type}_template.csv"
    
    response = requests.get(
        f"{API_V1}/import/{resource_type}/",
        headers=HEADERS,
        stream=True
    )
    
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_file


# ============================================
# 7. LEAD SCORING
# ============================================

def score_lead(lead_id):
    """Score a single lead"""
    payload = {
        "action": "score",
        "lead_id": lead_id
    }
    
    response = requests.post(
        f"{API_V1}/scoring/",
        headers=HEADERS,
        json=payload
    )
    return response.json()


def bulk_score_leads(lead_ids=None):
    """Score multiple leads in background"""
    payload = {
        "action": "bulk_score",
        "lead_ids": lead_ids or []  # Empty list scores all active leads
    }
    
    response = requests.post(
        f"{API_V1}/scoring/",
        headers=HEADERS,
        json=payload
    )
    return response.json()


def retrain_scoring_model():
    """Retrain the lead scoring model (admin only)"""
    payload = {
        "action": "retrain"
    }
    
    response = requests.post(
        f"{API_V1}/scoring/",
        headers=HEADERS,
        json=payload
    )
    return response.json()


def get_scoring_statistics():
    """Get lead scoring statistics"""
    response = requests.get(
        f"{API_V1}/scoring/",
        headers=HEADERS
    )
    return response.json()


# ============================================
# 8. WORKFLOWS
# ============================================

def create_workflow():
    """Create an automated workflow"""
    workflow_data = {
        "name": "Auto-assign high-value leads",
        "description": "Automatically assign leads with estimated value > $50k to senior sales rep",
        "trigger_type": "record_created",
        "trigger_conditions": {
            "model": "lead",
            "conditions": {
                "estimated_value__gte": 50000
            }
        },
        "actions": [
            {
                "type": "assign_record",
                "params": {
                    "user_id": 5
                }
            },
            {
                "type": "send_notification",
                "params": {
                    "message": "High-value lead assigned to you",
                    "user_id": 5
                }
            },
            {
                "type": "create_task",
                "params": {
                    "title": "Contact {{lead.first_name}} {{lead.last_name}}",
                    "due_days": 1,
                    "priority": "urgent"
                }
            }
        ],
        "status": "active"
    }
    
    response = requests.post(
        f"{API_V1}/workflows/",
        headers=HEADERS,
        json=workflow_data
    )
    return response.json()


def list_workflows(active_only=False):
    """List all workflows"""
    params = {"status": "active"} if active_only else {}
    
    response = requests.get(
        f"{API_V1}/workflows/",
        headers=HEADERS,
        params=params
    )
    return response.json()


def execute_workflow(workflow_id, trigger_data=None):
    """Manually execute a workflow"""
    payload = {
        "trigger_data": trigger_data or {}
    }
    
    response = requests.post(
        f"{API_V1}/workflows/{workflow_id}/execute/",
        headers=HEADERS,
        json=payload
    )
    return response.json()


def get_workflow_executions(workflow_id):
    """Get execution history for a workflow"""
    response = requests.get(
        f"{API_V1}/workflows/{workflow_id}/executions/",
        headers=HEADERS
    )
    return response.json()


# ============================================
# 9. NOTIFICATION TEMPLATES
# ============================================

def create_notification_template():
    """Create a notification template"""
    template_data = {
        "name": "Lead Assignment Notification",
        "notification_type": "email",
        "subject_template": "New Lead Assigned: {{lead.company_name}}",
        "body_template": """
        Hi {{user.first_name}},
        
        A new lead has been assigned to you:
        
        Name: {{lead.first_name}} {{lead.last_name}}
        Company: {{lead.company_name}}
        Email: {{lead.email}}
        Phone: {{lead.phone}}
        
        Please follow up within 24 hours.
        
        Best regards,
        MyCRM Team
        """,
        "variables": ["user.first_name", "lead.first_name", "lead.last_name", 
                     "lead.company_name", "lead.email", "lead.phone"],
        "is_active": True
    }
    
    response = requests.post(
        f"{API_V1}/notification-templates/",
        headers=HEADERS,
        json=template_data
    )
    return response.json()


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    # Get authentication token
    access_token, refresh_token = get_auth_token("admin", "password")
    TOKEN = access_token
    
    print("✅ Authentication successful")
    print(f"Access Token: {access_token[:20]}...")
    
    # Create a lead
    lead = create_lead()
    print(f"\n✅ Created lead: {lead['id']}")
    
    # Score the lead
    score_result = score_lead(lead['id'])
    print(f"✅ Lead scored: {score_result.get('score')}/100")
    
    # Search leads
    results = search_leads("Acme")
    print(f"\n✅ Found {results['count']} leads matching 'Acme'")
    
    # Get statistics
    stats = get_lead_statistics()
    print(f"\n✅ Lead Statistics:")
    print(f"   Total: {stats['total']}")
    print(f"   High Priority: {stats['by_priority']['high']}")
    
    # Import from CSV (example)
    # import_result = import_leads_from_csv("leads.csv")
    # print(f"\n✅ Imported {import_result['imported']} leads")
    
    # Export to CSV
    # export_file = export_leads_to_csv({"status": "qualified"})
    # print(f"\n✅ Exported leads to {export_file}")
    
    print("\n🎉 All examples completed successfully!")
