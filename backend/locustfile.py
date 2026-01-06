"""
Locust Load Testing Configuration for MyCRM
Run with: locust -f locustfile.py --host=http://localhost:8000
"""

from random import choice, randint

from locust import HttpUser, TaskSet, between, task


class ContactBehavior(TaskSet):
    """User behavior for contact management"""

    def on_start(self):
        """Login when starting"""
        # You'll need to implement actual authentication
        # For now, we'll assume the user is authenticated
        pass

    @task(3)
    def list_contacts(self):
        """List contacts - most common action"""
        self.client.get("/api/contacts/", name="List Contacts")

    @task(2)
    def view_contact(self):
        """View a specific contact"""
        contact_id = randint(1, 100)
        self.client.get(f"/api/contacts/{contact_id}/", name="View Contact")

    @task(1)
    def create_contact(self):
        """Create a new contact"""
        data = {
            "first_name": f"Test{randint(1000, 9999)}",
            "last_name": f"User{randint(1000, 9999)}",
            "email": f"test{randint(1000, 9999)}@example.com",
            "phone": f"+1234567{randint(100, 999)}",
            "company_name": f"Company{randint(1, 100)}",
            "contact_type": choice(["customer", "prospect", "vendor", "partner"])
        }
        self.client.post(
            "/api/contacts/",
            json=data,
            name="Create Contact"
        )

    @task(1)
    def update_contact(self):
        """Update a contact"""
        contact_id = randint(1, 50)
        data = {
            "first_name": f"Updated{randint(1000, 9999)}",
            "last_name": f"User{randint(1000, 9999)}",
            "email": f"updated{randint(1000, 9999)}@example.com"
        }
        self.client.put(
            f"/api/contacts/{contact_id}/",
            json=data,
            name="Update Contact"
        )

    @task(2)
    def search_contacts(self):
        """Search contacts"""
        search_terms = ["test", "user", "company", "john", "jane"]
        search = choice(search_terms)
        self.client.get(
            f"/api/contacts/?search={search}",
            name="Search Contacts"
        )


class LeadBehavior(TaskSet):
    """User behavior for lead management"""

    @task(3)
    def list_leads(self):
        """List leads"""
        self.client.get("/api/leads/", name="List Leads")

    @task(2)
    def view_lead(self):
        """View a specific lead"""
        lead_id = randint(1, 100)
        self.client.get(f"/api/leads/{lead_id}/", name="View Lead")

    @task(1)
    def create_lead(self):
        """Create a new lead"""
        data = {
            "first_name": f"Lead{randint(1000, 9999)}",
            "last_name": f"Test{randint(1000, 9999)}",
            "email": f"lead{randint(1000, 9999)}@example.com",
            "company_name": f"LeadCo{randint(1, 100)}",
            "status": choice(["new", "contacted", "qualified"]),
            "priority": choice(["low", "medium", "high"]),
            "lead_source": choice(["website", "referral", "social_media"])
        }
        self.client.post(
            "/api/leads/",
            json=data,
            name="Create Lead"
        )

    @task(1)
    def filter_leads_by_status(self):
        """Filter leads by status"""
        status = choice(["new", "contacted", "qualified", "converted"])
        self.client.get(
            f"/api/leads/?status={status}",
            name="Filter Leads"
        )


class OpportunityBehavior(TaskSet):
    """User behavior for opportunity management"""

    @task(3)
    def list_opportunities(self):
        """List opportunities"""
        self.client.get("/api/opportunities/", name="List Opportunities")

    @task(2)
    def view_opportunity(self):
        """View a specific opportunity"""
        opp_id = randint(1, 50)
        self.client.get(f"/api/opportunities/{opp_id}/", name="View Opportunity")

    @task(1)
    def create_opportunity(self):
        """Create a new opportunity"""
        data = {
            "name": f"Deal{randint(1000, 9999)}",
            "amount": randint(1000, 100000),
            "stage": choice(["prospecting", "qualification", "proposal", "negotiation"]),
            "probability": randint(0, 100)
        }
        self.client.post(
            "/api/opportunities/",
            json=data,
            name="Create Opportunity"
        )


class SalesUser(HttpUser):
    """Sales representative user behavior"""
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    tasks = {
        ContactBehavior: 3,
        LeadBehavior: 2,
        OpportunityBehavior: 1
    }

    def on_start(self):
        """Called when a simulated user starts"""
        # Implement authentication here if needed
        pass


class MarketingUser(HttpUser):
    """Marketing user behavior - mainly views data"""
    wait_time = between(2, 5)

    @task(5)
    def view_contacts(self):
        self.client.get("/api/contacts/", name="Marketing: View Contacts")

    @task(3)
    def view_leads(self):
        self.client.get("/api/leads/", name="Marketing: View Leads")

    @task(2)
    def view_campaigns(self):
        self.client.get("/api/campaigns/", name="Marketing: View Campaigns")

    @task(1)
    def view_reports(self):
        self.client.get("/api/reports/", name="Marketing: View Reports")


class ManagerUser(HttpUser):
    """Manager user behavior - mainly views reports and dashboards"""
    wait_time = between(3, 7)

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/dashboard/", name="Manager: Dashboard")

    @task(2)
    def view_reports(self):
        self.client.get("/api/reports/", name="Manager: Reports")

    @task(2)
    def view_analytics(self):
        self.client.get("/api/analytics/", name="Manager: Analytics")

    @task(1)
    def view_team_performance(self):
        self.client.get("/api/team/performance/", name="Manager: Team Performance")


class HeavyUser(HttpUser):
    """Simulates heavy system usage"""
    wait_time = between(0.5, 1.5)

    @task
    def stress_test(self):
        """Rapid fire requests"""
        endpoints = [
            "/api/contacts/",
            "/api/leads/",
            "/api/opportunities/",
            "/api/tasks/",
        ]
        for endpoint in endpoints:
            self.client.get(endpoint, name=f"Stress: {endpoint}")


# Load test scenarios
class LightLoad(HttpUser):
    """Light load scenario - Normal business hours"""
    wait_time = between(3, 10)
    tasks = [ContactBehavior, LeadBehavior]


class MediumLoad(HttpUser):
    """Medium load scenario - Peak hours"""
    wait_time = between(1, 5)
    tasks = {
        ContactBehavior: 3,
        LeadBehavior: 2,
        OpportunityBehavior: 1
    }


class HeavyLoad(HttpUser):
    """Heavy load scenario - Stress testing"""
    wait_time = between(0.5, 2)
    tasks = {
        ContactBehavior: 4,
        LeadBehavior: 3,
        OpportunityBehavior: 2
    }


"""
Run different scenarios:

1. Light Load Test (Normal usage):
   locust -f locustfile.py --users 10 --spawn-rate 2 --run-time 5m --html report_light.html

2. Medium Load Test (Peak hours):
   locust -f locustfile.py --users 50 --spawn-rate 5 --run-time 10m --html report_medium.html

3. Heavy Load Test (Stress test):
   locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 15m --html report_heavy.html

4. Spike Test (Sudden traffic):
   locust -f locustfile.py --users 200 --spawn-rate 50 --run-time 5m --html report_spike.html

5. Endurance Test (Long duration):
   locust -f locustfile.py --users 30 --spawn-rate 3 --run-time 2h --html report_endurance.html

6. Web UI (Interactive):
   locust -f locustfile.py --host=http://localhost:8000
   # Then open http://localhost:8089 in browser
"""
