# SLA (Service Level Agreement)

**Last Updated: January 4, 2026**

This Service Level Agreement ("SLA") describes the uptime commitments and support response times for MyCRM services.

---

## 1. Service Availability

### 1.1 Uptime Commitment

| Plan | Uptime Guarantee | Monthly Downtime Allowed | Service Credit |
|------|------------------|-------------------------|----------------|
| **Starter** | 99.5% | ~3.6 hours | 5% credit |
| **Professional** | 99.9% | ~43 minutes | 10% credit |
| **Enterprise** | 99.95% | ~22 minutes | 25% credit |
| **Custom** | 99.99% | ~4 minutes | Custom terms |

### 1.2 Uptime Definition

"Uptime" means the percentage of time the MyCRM platform is available and accessible to customers, calculated as:

```
Uptime % = ((Total Time - Downtime) / Total Time) × 100
```

**Measured monthly** from 00:00 UTC on the first day to 23:59 UTC on the last day.

### 1.3 Exclusions from Uptime

Downtime does NOT include:

**Scheduled Maintenance:**
- Announced 48 hours in advance
- Performed during maintenance window (see below)
- Maximum 4 hours per month

**Force Majeure:**
- Natural disasters
- War, terrorism, civil unrest
- Government actions
- Internet backbone failures
- Power grid failures

**Customer-Caused Issues:**
- Misuse of service
- Excessive API calls beyond limits
- Custom code or integrations
- Failure to update client software

**Third-Party Services:**
- Email provider outages (Gmail, Outlook)
- Payment processor issues
- DNS provider problems

**Beta Features:**
- Features marked "Beta" or "Preview"

### 1.4 Maintenance Windows

**Standard Maintenance:**
- **Day**: Sundays
- **Time**: 2:00 AM - 6:00 AM UTC
- **Frequency**: Up to 4 times per month
- **Notice**: 48 hours via email and in-app notification

**Emergency Maintenance:**
- Critical security patches
- Severe bug fixes
- As needed, with best-effort notice

### 1.5 Monitoring

**How we track uptime:**
- Automated health checks every 60 seconds
- Multi-region monitoring
- Third-party monitoring (Pingdom, StatusPage)
- Real user monitoring (RUM)

**Status Page:** [status.mycrm.app](https://status.mycrm.app)
- Real-time status
- Incident history
- Maintenance schedule
- Subscribe for alerts

---

## 2. Performance Commitments

### 2.1 Response Time

**API Response Time** (95th percentile):

| Endpoint Type | Target | Threshold |
|---------------|--------|-----------|
| Simple queries (GET) | < 200ms | < 500ms |
| Complex queries | < 500ms | < 1000ms |
| Create/Update (POST/PUT) | < 300ms | < 600ms |
| Reports | < 2s | < 5s |
| Bulk operations | < 5s | < 10s |

**Web App Page Load** (95th percentile):
- Initial load: < 2 seconds
- Navigation: < 500ms

### 2.2 Throughput

**API Rate Limits:**

| Plan | Requests per Hour | Burst Limit |
|------|------------------|-------------|
| **Starter** | 1,000 | 100 per minute |
| **Professional** | 10,000 | 500 per minute |
| **Enterprise** | 100,000 | 2,000 per minute |
| **Custom** | Negotiable | Negotiable |

**Exceeding limits:**
- 429 (Too Many Requests) response
- Retry-After header indicates wait time
- No charges for rate-limited requests

### 2.3 Database Performance

**Query Performance:**
- Simple queries: < 100ms
- Complex queries: < 500ms
- Report queries: < 2s

**Data Operations:**
- Create record: < 100ms
- Update record: < 150ms
- Delete record: < 100ms
- Bulk import (1000 records): < 30s

---

## 3. Support Response Times

### 3.1 Support Channels

| Plan | Email | Live Chat | Phone | Dedicated Manager |
|------|-------|-----------|-------|-------------------|
| **Starter** | ✅ | ✅ (business hours) | ❌ | ❌ |
| **Professional** | ✅ | ✅ (extended hours) | ❌ | ❌ |
| **Enterprise** | ✅ | ✅ (24/7) | ✅ | ✅ |

**Support Hours:**
- **Business Hours**: Monday-Friday, 9:00 AM - 6:00 PM ET
- **Extended Hours**: Monday-Friday, 7:00 AM - 10:00 PM ET
- **24/7**: All days, all hours

### 3.2 Priority Levels

**P1 - Critical:**
- Service completely unavailable
- Data loss or corruption
- Security breach
- Affects all or majority of users

**P2 - High:**
- Major feature broken
- Significant performance degradation
- Affects multiple users
- No workaround available

**P3 - Medium:**
- Feature partially working
- Moderate performance issues
- Affects single user or small group
- Workaround available

**P4 - Low:**
- Cosmetic issues
- Feature requests
- General questions
- Documentation errors

### 3.3 Response Time Commitments

**Starter Plan:**

| Priority | First Response | Resolution Target |
|----------|---------------|-------------------|
| P1 | 4 hours | 24 hours |
| P2 | 12 hours | 48 hours |
| P3 | 24 hours | 5 business days |
| P4 | 48 hours | 10 business days |

**Professional Plan:**

| Priority | First Response | Resolution Target |
|----------|---------------|-------------------|
| P1 | 2 hours | 12 hours |
| P2 | 4 hours | 24 hours |
| P3 | 8 hours | 3 business days |
| P4 | 24 hours | 7 business days |

**Enterprise Plan:**

| Priority | First Response | Resolution Target |
|----------|---------------|-------------------|
| P1 | 1 hour | 4 hours |
| P2 | 2 hours | 8 hours |
| P3 | 4 hours | 2 business days |
| P4 | 8 hours | 5 business days |

**Notes:**
- "First Response" = Initial acknowledgment from support team
- "Resolution Target" = Issue resolved or workaround provided
- Times measured during support hours (unless 24/7 plan)

---

## 4. Data Backup & Recovery

### 4.1 Backup Schedule

**Automated Backups:**
- **Full Backups**: Daily at 00:00 UTC
- **Incremental Backups**: Every 6 hours
- **Transaction Logs**: Continuous (RPO < 5 minutes)

### 4.2 Retention

| Backup Type | Retention Period |
|-------------|------------------|
| Daily backups | 30 days |
| Weekly backups | 90 days |
| Monthly backups | 1 year (Enterprise only) |

### 4.3 Recovery Objectives

**Recovery Point Objective (RPO):**
- Standard: < 6 hours
- Enterprise: < 15 minutes
- Custom: < 5 minutes

**Recovery Time Objective (RTO):**
- Standard: < 4 hours
- Enterprise: < 1 hour
- Custom: < 30 minutes

### 4.4 Disaster Recovery

**Multi-Region Redundancy:**
- Data replicated across 3 availability zones
- Automatic failover to healthy zones
- Active-active configuration (Enterprise)

**Disaster Recovery Plan:**
- Documented procedures
- Quarterly DR tests
- Annual full-scale DR exercises
- Results shared with Enterprise customers

---

## 5. Service Credits

### 5.1 Eligibility

You may request service credits if:
- Uptime falls below guaranteed percentage
- Properly report the downtime
- Request made within 30 days of incident

### 5.2 Credit Calculation

**Monthly Uptime vs. Credit:**

| Uptime % | Starter Credit | Professional Credit | Enterprise Credit |
|----------|---------------|---------------------|-------------------|
| < 99.0% | 5% | 10% | 25% |
| < 98.0% | 10% | 20% | 50% |
| < 97.0% | 15% | 30% | 75% |
| < 95.0% | 25% | 50% | 100% |

**Example:**
- Professional plan: $790/month (10 users × $79)
- Uptime: 98.5% (below 99.9% guarantee)
- Credit: 10% = $79

### 5.3 How to Request

**Submit via:**
- Email: sla@mycrm.app
- Subject: "SLA Credit Request - [Your Account ID]"
- Include:
  - Date and time of downtime (UTC)
  - Duration of downtime
  - Description of impact
  - Screenshot from status page (if available)

**Processing:**
- Reviewed within 5 business days
- Credits applied to next invoice
- No cash refunds (credits only)

### 5.4 Limitations

**Maximum credit per month:**
- Cannot exceed 100% of monthly subscription fee
- Applicable only to subscription fees (not usage or overage)
- Does not apply to free trial periods

**Sole Remedy:**
- Service credits are your SOLE remedy for downtime
- We are not liable for lost profits or consequential damages

---

## 6. Enterprise Additional Terms

### 6.1 Custom SLAs

Enterprise customers may negotiate:
- Higher uptime guarantees (up to 99.99%)
- Faster response times
- Dedicated infrastructure
- Priority support queuing
- Custom monitoring and alerting

### 6.2 Dedicated Support

**Customer Success Manager (CSM):**
- Single point of contact
- Quarterly business reviews
- Proactive account monitoring
- Feature planning assistance

**Technical Account Manager (TAM):**
- Deep technical expertise
- Architecture guidance
- Escalation management
- Hands-on troubleshooting

### 6.3 Service Level Reporting

**Monthly SLA Reports:**
- Uptime percentage
- Incident summary
- Performance metrics
- Support ticket analysis
- Trends and recommendations

---

## 7. Communication & Transparency

### 7.1 Incident Communication

**During Incidents:**
- Initial notification within 15 minutes (Enterprise: 5 minutes)
- Updates every 30 minutes until resolved
- Post-incident report within 48 hours

**Channels:**
- Email notifications
- Status page updates
- In-app banners (when accessible)
- SMS (Enterprise, opt-in)

### 7.2 Post-Incident Reports

**Includes:**
- Incident timeline
- Root cause analysis
- Impact assessment
- Remediation steps taken
- Preventive measures

**Available:**
- Published to status page
- Emailed to affected customers
- Enterprise: Detailed technical report

### 7.3 Maintenance Notifications

**Scheduled Maintenance:**
- 48 hours advance notice
- Maintenance window details
- Expected impact and duration
- Alternative arrangements (if any)

**Emergency Maintenance:**
- As much notice as possible (target: 2 hours)
- Reason for emergency work
- Expected duration

---

## 8. Security Commitments

### 8.1 Data Security

**Encryption:**
- TLS 1.3 in transit
- AES-256 at rest
- Encrypted backups

**Access Controls:**
- Multi-factor authentication available
- Role-based access control
- IP whitelisting (Enterprise)
- Audit logging

### 8.2 Compliance

**Certifications:**
- SOC 2 Type II (current)
- ISO 27001 (in progress)
- GDPR compliant
- HIPAA available (Enterprise)

**Audits:**
- Annual third-party security audits
- Penetration testing twice per year
- Results available to Enterprise customers

### 8.3 Vulnerability Management

**Response Times:**

| Severity | Patch Target |
|----------|--------------|
| Critical | 24 hours |
| High | 7 days |
| Medium | 30 days |
| Low | 90 days |

---

## 9. Changes to This SLA

### 9.1 Modifications

We may update this SLA:
- To reflect service improvements
- For legal or regulatory compliance
- To clarify existing terms

### 9.2 Notice

**Material changes:**
- 30 days advance notice via email
- Posted on website and in-app
- Customers may terminate if they object

**Non-material changes:**
- Effective upon posting
- "Last Updated" date changes

---

## 10. Contact

**SLA Questions:**
- Email: sla@mycrm.app
- Support: support@mycrm.app
- Enterprise: Your CSM or TAM

**Service Credits:**
- Email: sla@mycrm.app

**Status Page:**
- [status.mycrm.app](https://status.mycrm.app)

---

## 11. Definitions

**Availability**: The service is accessible and operational.

**Downtime**: Any period when the service is unavailable, excluding scheduled maintenance and force majeure.

**Business Day**: Monday through Friday, excluding US federal holidays.

**Business Hours**: Varies by plan (see Section 3.1).

**Incident**: Any event that causes service disruption or degradation.

**Maintenance**: Planned work to improve or maintain the service.

**Service Credit**: Discount applied to future invoices for SLA breaches.

---

**By using MyCRM, you agree to the terms outlined in this Service Level Agreement.**

---

**Version**: 2.0  
**Effective Date**: January 4, 2026
