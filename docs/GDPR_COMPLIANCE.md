# GDPR Compliance Documentation

**Last Updated: January 4, 2026**

This document outlines how MyCRM complies with the General Data Protection Regulation (GDPR) and other data protection laws.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Data Controller & Processor](#data-controller--processor)
3. [Lawful Basis for Processing](#lawful-basis-for-processing)
4. [Data Subject Rights](#data-subject-rights)
5. [Data Protection Principles](#data-protection-principles)
6. [Privacy by Design](#privacy-by-design)
7. [Data Breach Procedures](#data-breach-procedures)
8. [International Data Transfers](#international-data-transfers)
9. [Data Protection Impact Assessment](#data-protection-impact-assessment)
10. [Records of Processing Activities](#records-of-processing-activities)
11. [Compliance Measures](#compliance-measures)

---

## Overview

### Commitment to GDPR

MyCRM is fully committed to GDPR compliance. We process personal data in accordance with GDPR requirements and provide tools to help our customers meet their own GDPR obligations.

### Scope

GDPR applies to:
- **EU/EEA residents**: Regardless of where processing occurs
- **UK residents**: Under UK GDPR (post-Brexit)
- **Data processed in EU**: Regardless of data subject location

### Key Definitions

- **Personal Data**: Any information relating to an identified or identifiable natural person
- **Data Subject**: The individual whose personal data is processed
- **Data Controller**: Entity that determines purposes and means of processing
- **Data Processor**: Entity that processes data on behalf of the controller
- **Processing**: Any operation performed on personal data

---

## Data Controller & Processor

### Our Role

**MyCRM acts as a Data Processor:**
- You (our customer) are the Data Controller for customer data you store in MyCRM
- We process data according to your instructions
- We are the Data Controller for account and usage data

### Your Responsibilities as Controller

When using MyCRM, you are responsible for:
- ✅ Lawfully collecting personal data
- ✅ Obtaining necessary consents
- ✅ Providing privacy notices to your customers
- ✅ Honoring data subject rights requests
- ✅ Ensuring data accuracy
- ✅ Implementing appropriate security measures
- ✅ Reporting data breaches (when required)

### Our Responsibilities as Processor

We commit to:
- ✅ Process data only on your documented instructions
- ✅ Ensure confidentiality of processing personnel
- ✅ Implement appropriate technical and organizational measures
- ✅ Assist with data subject rights requests
- ✅ Assist with data breach notifications
- ✅ Delete or return data upon contract termination
- ✅ Provide information necessary to demonstrate compliance
- ✅ Use sub-processors only with your authorization

### Data Processing Agreement (DPA)

We offer a **Data Processing Agreement** that includes:
- Processing instructions and scope
- Data subject rights assistance
- Security measures
- Sub-processor list
- International data transfer mechanisms
- Audit rights

**Enterprise customers**: DPA included in contract.  
**Other plans**: Standard DPA available at [https://mycrm.app/dpa](https://mycrm.app/dpa)

---

## Lawful Basis for Processing

### Account Data (We are Controller)

| Data Type | Lawful Basis | Purpose |
|-----------|--------------|---------|
| Account information (name, email) | Contract | Provide the service |
| Payment information | Contract | Process payments |
| Usage data | Legitimate interests | Improve service, security |
| Marketing communications | Consent | Send promotional content |
| Support communications | Contract | Provide customer support |
| Security logs | Legitimate interests | Detect fraud, ensure security |

### Customer Data (You are Controller)

For data you store about your customers (leads, contacts, etc.), **you must determine the lawful basis**, such as:
- **Consent**: Customer explicitly agrees
- **Contract**: Necessary to fulfill a contract
- **Legal obligation**: Required by law
- **Legitimate interests**: Your business interests (balanced against rights)
- **Vital interests**: Protect someone's life
- **Public task**: Performing a task in the public interest

### Consent Management

When relying on consent:
- ✅ Must be freely given, specific, informed, and unambiguous
- ✅ Must be easy to withdraw
- ✅ Children under 16 require parental consent (varies by country)
- ✅ Keep records of consent

**Our tools:**
- Consent tracking fields in MyCRM
- Consent timestamp logging
- Opt-in/opt-out management
- Audit trail of consent changes

---

## Data Subject Rights

### Rights Under GDPR

Data subjects have the following rights:

#### 1. Right to Be Informed (Art. 13-14)

**What:** Know how their data is processed.

**How we support:**
- Transparent [Privacy Policy](/docs/PRIVACY_POLICY.md)
- Clear consent forms
- Privacy notices at collection points

#### 2. Right of Access (Art. 15)

**What:** Obtain confirmation if data is processed and access their data.

**How we support:**
- Self-service data export: Settings → Export Data
- Formatted data report (JSON, CSV)
- Copy of data provided within 30 days

#### 3. Right to Rectification (Art. 16)

**What:** Correct inaccurate or incomplete data.

**How we support:**
- Users can update their own data in Settings
- Admins can update customer data
- Bulk update tools available

#### 4. Right to Erasure / "Right to be Forgotten" (Art. 17)

**What:** Request deletion of personal data.

**How we support:**
- Self-service account deletion: Settings → Delete Account
- Data permanently deleted after 90-day recovery period
- Deletion cascades to all related data
- Exceptions: Legal obligations, public interest

**Process:**
1. User requests deletion
2. Account deactivated immediately
3. 90-day recovery period (user can restore)
4. After 90 days: Permanent deletion
5. Backups purged within 180 days

#### 5. Right to Restriction of Processing (Art. 18)

**What:** Limit how data is processed.

**How we support:**
- Account suspension (data retained but not processed)
- Export-only mode
- Processing restriction flags
- Contact privacy@mycrm.app to request

#### 6. Right to Data Portability (Art. 20)

**What:** Receive data in a structured, machine-readable format.

**How we support:**
- Export in CSV format (human-readable)
- Export in JSON format (machine-readable)
- API access for automated transfers
- Includes all personal data you provided

#### 7. Right to Object (Art. 21)

**What:** Object to processing based on legitimate interests or for direct marketing.

**How we support:**
- Opt-out of marketing: Unsubscribe links in emails
- Opt-out of analytics: Settings → Privacy → Analytics
- Object to processing: Contact privacy@mycrm.app

#### 8. Rights Related to Automated Decision-Making (Art. 22)

**What:** Not be subject to decisions based solely on automated processing with legal/significant effects.

**How we support:**
- AI lead scoring is advisory, not deterministic
- Human review available for significant decisions
- Transparency about AI usage
- Right to human intervention

### Exercising Rights

**How to submit requests:**
- Email: privacy@mycrm.app
- In-app: Settings → Privacy → Data Rights Request
- Postal mail: [Your Business Address]

**Include in request:**
- Full name
- Email address associated with account
- Specific right you wish to exercise
- Any relevant details

**Response time:**
- Within 30 days (may extend to 60 days for complex requests)
- Free of charge (unless requests are excessive)
- Identity verification required

### Identity Verification

To protect your privacy, we verify your identity before fulfilling requests:
- Confirm email address
- Security questions
- Two-factor authentication
- Photo ID (for sensitive requests)

---

## Data Protection Principles

### 1. Lawfulness, Fairness, Transparency

**We commit to:**
- Process data lawfully with appropriate legal basis
- Be transparent about what data we collect and why
- Provide clear privacy notices
- No hidden data collection

### 2. Purpose Limitation

**We commit to:**
- Collect data only for specified, explicit purposes
- Not process data in ways incompatible with original purpose
- Document purposes for all processing activities

### 3. Data Minimization

**We commit to:**
- Collect only data necessary for stated purposes
- Not collect "nice to have" data
- Regular review of data collected
- Remove unnecessary fields

### 4. Accuracy

**We commit to:**
- Keep data accurate and up-to-date
- Provide tools for users to correct data
- Delete or rectify inaccurate data promptly
- Regular data quality reviews

### 5. Storage Limitation

**We commit to:**
- Retain data only as long as necessary
- Delete data when no longer needed
- Clear retention schedules (see [Data Retention](#data-retention))
- Automated deletion processes

### 6. Integrity and Confidentiality (Security)

**We commit to:**
- Implement appropriate security measures (see [Security](#security-measures))
- Protect against unauthorized access, loss, or destruction
- Regular security audits and testing
- Incident response procedures

### 7. Accountability

**We commit to:**
- Demonstrate compliance with GDPR
- Maintain documentation of processing activities
- Implement appropriate policies and procedures
- Train staff on data protection
- Appoint a Data Protection Officer (DPO)

---

## Privacy by Design

### Principles

We embed data protection into our development process:

#### 1. Proactive not Reactive

- Consider privacy before launching features
- Anticipate privacy risks
- Prevent privacy breaches before they occur

#### 2. Privacy as Default

- Strongest privacy settings by default
- Users don't need to take action to protect privacy
- Opt-in, not opt-out, for non-essential processing

#### 3. Privacy Embedded into Design

- Privacy integral to system design
- Not an add-on or afterthought
- Full functionality with privacy protection

#### 4. Positive-Sum (Win-Win)

- No false trade-offs (e.g., privacy vs. security)
- Achieve all legitimate objectives

#### 5. End-to-End Security

- Data protected throughout entire lifecycle
- Secure collection, storage, use, and deletion
- Strong encryption and access controls

#### 6. Visibility and Transparency

- Operations remain visible to users
- Clear privacy practices
- Independent verification available

#### 7. Respect for User Privacy

- User-centric design
- Easy-to-use privacy controls
- Clear communication

### Implementation

**In development:**
- Privacy impact assessments for new features
- Secure coding standards
- Code reviews focused on privacy
- Testing for privacy compliance

**In operations:**
- Regular privacy audits
- Incident response procedures
- Employee training
- Third-party vendor assessments

---

## Data Breach Procedures

### Detection

**Monitoring:**
- 24/7 security monitoring
- Automated intrusion detection
- Log analysis and alerting
- User report mechanisms

### Assessment

**Upon detecting a potential breach:**

1. **Contain** the breach immediately
2. **Assess** scope and severity:
   - What data was affected?
   - How many data subjects?
   - What is the risk to individuals?
3. **Document** all findings

### Notification

**To Supervisory Authority (if required):**
- Within 72 hours of becoming aware
- Via appropriate channels (varies by country)
- Include:
  - Nature of breach
  - Categories and approximate number of data subjects
  - Likely consequences
  - Measures taken or proposed

**To Data Subjects (if high risk):**
- Without undue delay
- In clear, plain language
- Include:
  - Description of breach
  - Contact point for more information
  - Likely consequences
  - Measures taken
  - Recommendations to mitigate risk

**To Customers (Data Controllers):**
- Immediate notification
- Full incident details
- Assistance with their notification obligations

### Resolution

**Response actions:**
1. Fix vulnerability
2. Restore secure state
3. Conduct post-incident review
4. Update procedures to prevent recurrence
5. Document lessons learned

### Your Obligations

**As a Data Controller using our service:**
- You must notify your supervisory authority (if required)
- You must notify affected data subjects (if required)
- We will assist by providing necessary information
- Maintain your own incident response plan

---

## International Data Transfers

### Data Residency

**We offer data storage in multiple regions:**
- 🇺🇸 United States (AWS us-east-1)
- 🇪🇺 European Union (AWS eu-central-1, Frankfurt)
- 🇬🇧 United Kingdom (AWS eu-west-2, London)
- 🇸🇬 Asia-Pacific (AWS ap-southeast-1, Singapore)
- 🇦🇺 Australia (AWS ap-southeast-2, Sydney)

**You choose your data region during signup.** Data stays in your selected region.

### Transfer Mechanisms

**When data must be transferred outside EU/EEA:**

#### 1. Standard Contractual Clauses (SCCs)

- EU Commission-approved SCCs (2021 version)
- Contractual safeguards for data transfers
- Included in our DPA

#### 2. Adequacy Decisions

- Transfers to countries deemed "adequate" by EU Commission
- Currently: 🇬🇧 UK (post-Brexit), 🇨🇭 Switzerland, 🇨🇦 Canada, 🇯🇵 Japan, and others

#### 3. Binding Corporate Rules (BCRs)

- Internal policies approved by supervisory authorities
- For intra-company transfers

#### 4. Derogations (Specific Situations)

- Explicit consent
- Contract performance
- Legal claims
- Public interest

### Sub-Processors

**We use sub-processors in various locations. All are contractually bound by:**
- GDPR-compliant agreements
- Standard Contractual Clauses (where applicable)
- Appropriate security measures

**Sub-processor list:**

| Sub-Processor | Service | Location | Transfer Mechanism |
|---------------|---------|----------|-------------------|
| Amazon Web Services | Hosting | US, EU, UK | SCCs |
| SendGrid | Email delivery | US | SCCs |
| Stripe | Payment processing | US | SCCs |
| Cloudflare | CDN, Security | Global | SCCs |
| Google | Analytics | US | SCCs |
| Zendesk | Support | US | SCCs |

**Full list and updates:** [https://mycrm.app/sub-processors](https://mycrm.app/sub-processors)

**We notify you before adding new sub-processors** (30 days notice). You may object.

---

## Data Protection Impact Assessment

### When We Conduct DPIAs

We conduct Data Protection Impact Assessments for:
- New features involving personal data
- High-risk processing activities
- Systematic monitoring
- Large-scale processing of special categories of data
- Automated decision-making
- New technologies

### DPIA Process

1. **Describe** processing and purposes
2. **Assess** necessity and proportionality
3. **Identify** risks to data subjects
4. **Evaluate** likelihood and severity
5. **Identify** measures to mitigate risks
6. **Document** outcomes and decisions
7. **Review** and update regularly

### Consultation

If high risk remains after mitigation:
- Consult supervisory authority before processing
- Await guidance or approval

---

## Records of Processing Activities

We maintain detailed records of processing activities (Art. 30 GDPR):

### Information Recorded

**As Data Controller (account data):**
- Controller contact details and DPO
- Purposes of processing
- Categories of data subjects and data
- Categories of recipients (including third countries)
- Transfer mechanisms and safeguards
- Retention periods
- Security measures

**As Data Processor (customer data):**
- Processor contact details and DPO
- Categories of processing activities
- Processing on behalf of which controllers
- International transfers
- Security measures

### Availability

Records available to supervisory authorities upon request.

**Enterprise customers** may request copies of relevant records.

---

## Compliance Measures

### Data Protection Officer (DPO)

**Our DPO:**
- Email: dpo@mycrm.app
- Responsible for monitoring GDPR compliance
- Advises on data protection obligations
- Cooperates with supervisory authorities
- Point of contact for data subjects

### Policies and Procedures

**We maintain:**
- ✅ Privacy Policy
- ✅ Data Protection Policy (internal)
- ✅ Data Retention Policy
- ✅ Data Breach Response Plan
- ✅ Data Subject Rights Procedures
- ✅ Vendor Management Policy
- ✅ Security Policies
- ✅ Employee Data Protection Training

### Training

**All employees receive:**
- GDPR awareness training (onboarding)
- Annual refresher training
- Role-specific training (developers, support, etc.)
- Incident response training

### Audits and Certification

**Regular assessments:**
- Internal privacy audits (quarterly)
- External security audits (annual)
- Penetration testing (bi-annual)
- SOC 2 Type II certification
- ISO 27001 compliance (in progress)

### Supervisory Authority

**Our lead supervisory authority:**
- [Relevant Data Protection Authority based on your location]

**For EU customers:**
- Work with your local supervisory authority
- We cooperate with all EU DPAs

---

## Tools for Your Compliance

### Built-in Features

**We provide tools to help you comply with GDPR:**

1. **Consent Management**
   - Capture consent with timestamp
   - Track consent versions
   - Easy opt-in/opt-out
   - Audit trail

2. **Data Subject Rights**
   - Export data (JSON, CSV)
   - Delete data (right to erasure)
   - Rectify data (easy editing)
   - Restrict processing (suspend account)

3. **Data Portability**
   - One-click export
   - Machine-readable formats
   - API access

4. **Privacy Controls**
   - Field-level encryption
   - Access controls (RBAC)
   - Audit logs
   - Data retention settings

5. **Security Features**
   - Two-factor authentication
   - IP whitelisting
   - Session management
   - Encryption at rest and in transit

### Documentation Support

**We provide:**
- Sample privacy notices
- Consent form templates
- Data processing records templates
- DPA (Data Processing Agreement)
- Sub-processor information

---

## FAQ

### Q: Do I need a DPA with MyCRM?

**A:** Yes, if you're a Data Controller and we process personal data on your behalf. We provide a standard DPA for all customers.

### Q: Where is my data stored?

**A:** In the region you selected during signup. Data doesn't leave that region (except for authorized sub-processors with SCCs).

### Q: How do I handle data subject requests?

**A:** For data in MyCRM:
1. Use built-in export/delete tools
2. Contact support for assistance
3. We'll help retrieve or delete data within 30 days

### Q: What if there's a data breach?

**A:** We'll notify you within 72 hours and provide all details needed for your own breach notification obligations.

### Q: Can I audit your compliance?

**A:** Enterprise customers have audit rights per DPA. We also provide:
- SOC 2 reports
- Security questionnaires
- Compliance certifications

### Q: Do you process children's data?

**A:** MyCRM is not designed for children under 16. If you collect children's data, you must obtain parental consent and comply with additional requirements.

### Q: What about special categories of data (sensitive data)?

**A:** We recommend NOT storing special categories (health, biometric, genetic, etc.) unless absolutely necessary and with explicit consent. Contact us for guidance.

---

## Contact

**GDPR Questions:**
- Data Protection Officer: dpo@mycrm.app
- Privacy Team: privacy@mycrm.app
- General Support: support@mycrm.app

**Address:**
[Your Business Address]

---

**Last Updated**: January 4, 2026  
**Version**: 2.0  
**Next Review**: July 2026
