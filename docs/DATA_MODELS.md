# 📊 MyCRM Data Models

## Overview

This document provides comprehensive documentation for all data models in the MyCRM platform. Models are organized by domain and include field definitions, relationships, and usage notes.

---

## 🏢 Organization & Multi-Tenancy

### Organization

The root entity for multi-tenant data isolation.

```
┌─────────────────────────────────────────────────────────────┐
│                      Organization                            │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Organization name       │
│ slug            │ VARCHAR(100)    │ URL-safe identifier     │
│ logo_url        │ VARCHAR(500)    │ Logo image URL          │
│ plan            │ ENUM            │ starter/pro/enterprise  │
│ settings        │ JSONB           │ Organization settings   │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
│ is_active       │ BOOLEAN         │ Active status           │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (slug)                                             │
│ • INDEX (plan, is_active)                                   │
└─────────────────────────────────────────────────────────────┘

Relationships:
• One-to-Many: Users, Contacts, Leads, Opportunities, etc.
```

---

## 👤 User Management

### User

Extended Django user model with CRM-specific fields.

```
┌─────────────────────────────────────────────────────────────┐
│                          User                                │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ email           │ VARCHAR(254)    │ Email (login)           │
│ password        │ VARCHAR(128)    │ Hashed password         │
│ first_name      │ VARCHAR(150)    │ First name              │
│ last_name       │ VARCHAR(150)    │ Last name               │
│ phone           │ VARCHAR(20)     │ Phone number            │
│ avatar_url      │ VARCHAR(500)    │ Profile photo URL       │
│ role            │ ENUM            │ User role               │
│ job_title       │ VARCHAR(100)    │ Job title               │
│ department      │ VARCHAR(100)    │ Department              │
│ timezone        │ VARCHAR(50)     │ User timezone           │
│ locale          │ VARCHAR(10)     │ Language preference     │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ team_id         │ UUID (FK)       │ Team assignment         │
│ manager_id      │ UUID (FK)       │ Reporting manager       │
│ is_active       │ BOOLEAN         │ Account active          │
│ is_staff        │ BOOLEAN         │ Staff access            │
│ is_superuser    │ BOOLEAN         │ Superuser access        │
│ mfa_enabled     │ BOOLEAN         │ MFA status              │
│ mfa_secret      │ VARCHAR(255)    │ TOTP secret (encrypted) │
│ last_login      │ TIMESTAMP       │ Last login time         │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (email)                                            │
│ • INDEX (organization_id, role)                             │
│ • INDEX (team_id)                                           │
│ • INDEX (manager_id)                                        │
└─────────────────────────────────────────────────────────────┘

Relationships:
• Many-to-One: Organization, Team
• One-to-Many: Contacts, Leads, Opportunities (as owner)
• Self-referential: Manager (reports_to)

Role Values:
• super_admin - Platform administrator
• admin - Organization administrator
• manager - Team manager
• sales_rep - Sales representative
• marketing - Marketing user
• readonly - View-only access
```

### Team

Logical grouping of users within an organization.

```
┌─────────────────────────────────────────────────────────────┐
│                          Team                                │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Team name               │
│ description     │ TEXT            │ Team description        │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ lead_id         │ UUID (FK)       │ Team lead (User)        │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (organization_id, name)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📇 Contact Management

### Contact

Primary entity for storing customer/prospect contact information.

```
┌─────────────────────────────────────────────────────────────┐
│                        Contact                               │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ first_name      │ VARCHAR(100)    │ First name              │
│ last_name       │ VARCHAR(100)    │ Last name               │
│ email           │ VARCHAR(254)    │ Primary email           │
│ phone           │ VARCHAR(20)     │ Primary phone           │
│ mobile          │ VARCHAR(20)     │ Mobile phone            │
│ company         │ VARCHAR(255)    │ Company name            │
│ job_title       │ VARCHAR(100)    │ Job title               │
│ department      │ VARCHAR(100)    │ Department              │
│ website         │ VARCHAR(500)    │ Personal/company website│
│ linkedin_url    │ VARCHAR(500)    │ LinkedIn profile        │
│ twitter_handle  │ VARCHAR(50)     │ Twitter handle          │
│ address_line1   │ VARCHAR(255)    │ Street address          │
│ address_line2   │ VARCHAR(255)    │ Address line 2          │
│ city            │ VARCHAR(100)    │ City                    │
│ state           │ VARCHAR(100)    │ State/Province          │
│ postal_code     │ VARCHAR(20)     │ ZIP/Postal code         │
│ country         │ VARCHAR(2)      │ ISO country code        │
│ status          │ ENUM            │ active/inactive/archived│
│ source          │ ENUM            │ Lead source             │
│ lifecycle_stage │ ENUM            │ subscriber/lead/customer│
│ tags            │ JSONB           │ Array of tags           │
│ custom_fields   │ JSONB           │ Custom field values     │
│ score           │ INTEGER         │ Contact score (0-100)   │
│ owner_id        │ UUID (FK)       │ Contact owner (User)    │
│ assigned_to_id  │ UUID (FK)       │ Assigned user           │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ company_id      │ UUID (FK)       │ Company entity          │
│ last_activity_at│ TIMESTAMP       │ Last interaction        │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
│ is_deleted      │ BOOLEAN         │ Soft delete flag        │
│ deleted_at      │ TIMESTAMP       │ Deletion timestamp      │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (organization_id, email)                            │
│ • INDEX (organization_id, company)                          │
│ • INDEX (owner_id)                                          │
│ • INDEX (status, lifecycle_stage)                           │
│ • INDEX (created_at)                                        │
│ • INDEX (score)                                             │
│ • GIN INDEX (tags)                                          │
│ • FULL TEXT INDEX (first_name, last_name, email, company)   │
└─────────────────────────────────────────────────────────────┘

Relationships:
• Many-to-One: Organization, User (owner), Company
• One-to-Many: Leads, Opportunities, Activities, Notes
```

### Company (Account)

Company/Account entity for B2B relationships.

```
┌─────────────────────────────────────────────────────────────┐
│                        Company                               │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Company name            │
│ domain          │ VARCHAR(255)    │ Primary domain          │
│ industry        │ VARCHAR(100)    │ Industry vertical       │
│ company_size    │ ENUM            │ Size range              │
│ annual_revenue  │ DECIMAL(15,2)   │ Annual revenue          │
│ founded_year    │ INTEGER         │ Year founded            │
│ description     │ TEXT            │ Company description     │
│ logo_url        │ VARCHAR(500)    │ Company logo URL        │
│ website         │ VARCHAR(500)    │ Company website         │
│ linkedin_url    │ VARCHAR(500)    │ LinkedIn page           │
│ address_line1   │ VARCHAR(255)    │ HQ address              │
│ city            │ VARCHAR(100)    │ City                    │
│ state           │ VARCHAR(100)    │ State/Province          │
│ country         │ VARCHAR(2)      │ ISO country code        │
│ phone           │ VARCHAR(20)     │ Main phone              │
│ employee_count  │ INTEGER         │ Number of employees     │
│ type            │ ENUM            │ prospect/customer/etc   │
│ tier            │ ENUM            │ Account tier            │
│ health_score    │ INTEGER         │ Health score (0-100)    │
│ owner_id        │ UUID (FK)       │ Account owner           │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ custom_fields   │ JSONB           │ Custom field values     │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (organization_id, domain)                          │
│ • INDEX (organization_id, name)                             │
│ • INDEX (industry)                                          │
│ • INDEX (owner_id)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎣 Lead Management

### Lead

Prospective customer before qualification.

```
┌─────────────────────────────────────────────────────────────┐
│                          Lead                                │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Lead name/title         │
│ first_name      │ VARCHAR(100)    │ Contact first name      │
│ last_name       │ VARCHAR(100)    │ Contact last name       │
│ email           │ VARCHAR(254)    │ Email address           │
│ phone           │ VARCHAR(20)     │ Phone number            │
│ company         │ VARCHAR(255)    │ Company name            │
│ job_title       │ VARCHAR(100)    │ Job title               │
│ website         │ VARCHAR(500)    │ Website URL             │
│ source          │ ENUM            │ Lead source             │
│ source_detail   │ VARCHAR(255)    │ Source specifics        │
│ status          │ ENUM            │ Lead status             │
│ substatus       │ VARCHAR(50)     │ Status detail           │
│ score           │ INTEGER         │ Lead score (0-100)      │
│ score_breakdown │ JSONB           │ Score components        │
│ grade           │ CHAR(1)         │ Lead grade (A-F)        │
│ estimated_value │ DECIMAL(15,2)   │ Potential deal value    │
│ probability     │ DECIMAL(3,2)    │ Conversion probability  │
│ utm_source      │ VARCHAR(100)    │ UTM source              │
│ utm_medium      │ VARCHAR(100)    │ UTM medium              │
│ utm_campaign    │ VARCHAR(100)    │ UTM campaign            │
│ referrer_url    │ VARCHAR(500)    │ Referrer URL            │
│ landing_page    │ VARCHAR(500)    │ Landing page URL        │
│ notes           │ TEXT            │ Internal notes          │
│ tags            │ JSONB           │ Array of tags           │
│ custom_fields   │ JSONB           │ Custom field values     │
│ owner_id        │ UUID (FK)       │ Lead owner              │
│ assigned_to_id  │ UUID (FK)       │ Assigned sales rep      │
│ converted_contact_id │ UUID (FK) │ Converted contact       │
│ converted_opportunity_id │ UUID  │ Converted opportunity   │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ campaign_id     │ UUID (FK)       │ Source campaign         │
│ last_activity_at│ TIMESTAMP       │ Last interaction        │
│ first_responded_at│ TIMESTAMP     │ First response time     │
│ qualified_at    │ TIMESTAMP       │ Qualification time      │
│ converted_at    │ TIMESTAMP       │ Conversion time         │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
│ is_deleted      │ BOOLEAN         │ Soft delete flag        │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (organization_id, email)                            │
│ • INDEX (organization_id, status)                           │
│ • INDEX (owner_id)                                          │
│ • INDEX (assigned_to_id)                                    │
│ • INDEX (source, status)                                    │
│ • INDEX (score DESC)                                        │
│ • INDEX (created_at)                                        │
│ • GIN INDEX (tags)                                          │
└─────────────────────────────────────────────────────────────┘

Status Values:
• new - Newly created
• contacted - Initial contact made
• engaged - Responding to outreach
• qualified - Meets qualification criteria
• converted - Converted to opportunity
• disqualified - Does not meet criteria
• nurturing - Long-term nurture

Source Values:
• website - Website form
• referral - Customer/partner referral
• cold_call - Outbound call
• cold_email - Outbound email
• event - Trade show/conference
• social - Social media
• paid_ads - Paid advertising
• organic - Organic search
• partner - Partner channel
• other - Other source
```

---

## 💼 Opportunity Management

### Pipeline

Sales pipeline configuration.

```
┌─────────────────────────────────────────────────────────────┐
│                        Pipeline                              │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Pipeline name           │
│ description     │ TEXT            │ Description             │
│ is_default      │ BOOLEAN         │ Default pipeline        │
│ is_active       │ BOOLEAN         │ Active status           │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (organization_id, name)                            │
│ • INDEX (organization_id, is_active)                        │
└─────────────────────────────────────────────────────────────┘
```

### Stage

Pipeline stages for opportunity progression.

```
┌─────────────────────────────────────────────────────────────┐
│                         Stage                                │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(100)    │ Stage name              │
│ probability     │ INTEGER         │ Win probability (0-100) │
│ order           │ INTEGER         │ Display order           │
│ color           │ VARCHAR(7)      │ Hex color code          │
│ description     │ TEXT            │ Stage description       │
│ is_won          │ BOOLEAN         │ Closed won stage        │
│ is_lost         │ BOOLEAN         │ Closed lost stage       │
│ pipeline_id     │ UUID (FK)       │ Parent pipeline         │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • UNIQUE (pipeline_id, name)                                │
│ • INDEX (pipeline_id, order)                                │
└─────────────────────────────────────────────────────────────┘
```

### Opportunity

Sales opportunity/deal tracking.

```
┌─────────────────────────────────────────────────────────────┐
│                      Opportunity                             │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ name            │ VARCHAR(255)    │ Deal name               │
│ description     │ TEXT            │ Deal description        │
│ value           │ DECIMAL(15,2)   │ Deal value              │
│ currency        │ VARCHAR(3)      │ ISO currency code       │
│ probability     │ DECIMAL(3,2)    │ Win probability         │
│ weighted_value  │ DECIMAL(15,2)   │ value × probability     │
│ expected_close_date │ DATE        │ Expected close date     │
│ actual_close_date │ DATE          │ Actual close date       │
│ stage_id        │ UUID (FK)       │ Current stage           │
│ pipeline_id     │ UUID (FK)       │ Pipeline                │
│ contact_id      │ UUID (FK)       │ Primary contact         │
│ company_id      │ UUID (FK)       │ Company/Account         │
│ lead_id         │ UUID (FK)       │ Source lead             │
│ owner_id        │ UUID (FK)       │ Deal owner              │
│ status          │ ENUM            │ open/won/lost           │
│ loss_reason     │ VARCHAR(255)    │ Reason if lost          │
│ competitor      │ VARCHAR(255)    │ Competitor (if lost)    │
│ next_step       │ TEXT            │ Next action             │
│ tags            │ JSONB           │ Array of tags           │
│ custom_fields   │ JSONB           │ Custom field values     │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ last_activity_at│ TIMESTAMP       │ Last interaction        │
│ days_in_stage   │ INTEGER         │ Days in current stage   │
│ stage_changed_at│ TIMESTAMP       │ Last stage change       │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
│ is_deleted      │ BOOLEAN         │ Soft delete flag        │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (organization_id, status)                           │
│ • INDEX (organization_id, pipeline_id, stage_id)            │
│ • INDEX (owner_id)                                          │
│ • INDEX (contact_id)                                        │
│ • INDEX (expected_close_date)                               │
│ • INDEX (value DESC)                                        │
│ • INDEX (created_at)                                        │
│ • GIN INDEX (tags)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Task Management

### Task

Task and activity tracking.

```
┌─────────────────────────────────────────────────────────────┐
│                          Task                                │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ title           │ VARCHAR(255)    │ Task title              │
│ description     │ TEXT            │ Task description        │
│ task_type       │ ENUM            │ Type of task            │
│ priority        │ ENUM            │ Priority level          │
│ status          │ ENUM            │ Task status             │
│ due_date        │ TIMESTAMP       │ Due date/time           │
│ reminder_at     │ TIMESTAMP       │ Reminder time           │
│ completed_at    │ TIMESTAMP       │ Completion time         │
│ outcome         │ VARCHAR(255)    │ Task outcome            │
│ notes           │ TEXT            │ Completion notes        │
│ assigned_to_id  │ UUID (FK)       │ Assigned user           │
│ created_by_id   │ UUID (FK)       │ Created by user         │
│ contact_id      │ UUID (FK)       │ Related contact         │
│ lead_id         │ UUID (FK)       │ Related lead            │
│ opportunity_id  │ UUID (FK)       │ Related opportunity     │
│ company_id      │ UUID (FK)       │ Related company         │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ is_recurring    │ BOOLEAN         │ Recurring task flag     │
│ recurrence_rule │ VARCHAR(255)    │ iCal RRULE format       │
│ parent_task_id  │ UUID (FK)       │ Parent recurring task   │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
│ updated_at      │ TIMESTAMP       │ Last update timestamp   │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (assigned_to_id, status)                            │
│ • INDEX (due_date)                                          │
│ • INDEX (organization_id, status, due_date)                 │
│ • INDEX (contact_id)                                        │
│ • INDEX (opportunity_id)                                    │
└─────────────────────────────────────────────────────────────┘

Task Type Values:
• call - Phone call
• email - Send email
• meeting - Schedule meeting
• follow_up - Follow up
• demo - Product demo
• proposal - Send proposal
• other - Other task

Priority Values:
• low - Low priority
• medium - Medium priority
• high - High priority
• urgent - Urgent priority

Status Values:
• pending - Not started
• in_progress - In progress
• completed - Completed
• cancelled - Cancelled
```

---

## 📧 Communication

### EmailTracking

Email interaction tracking.

```
┌─────────────────────────────────────────────────────────────┐
│                     EmailTracking                            │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ subject         │ VARCHAR(500)    │ Email subject           │
│ body_preview    │ TEXT            │ Body preview            │
│ from_email      │ VARCHAR(254)    │ Sender email            │
│ to_email        │ VARCHAR(254)    │ Recipient email         │
│ message_id      │ VARCHAR(255)    │ Email message ID        │
│ thread_id       │ VARCHAR(255)    │ Thread ID               │
│ sent_at         │ TIMESTAMP       │ Send timestamp          │
│ opened_at       │ TIMESTAMP       │ First open              │
│ open_count      │ INTEGER         │ Total opens             │
│ clicked_at      │ TIMESTAMP       │ First click             │
│ click_count     │ INTEGER         │ Total clicks            │
│ replied_at      │ TIMESTAMP       │ Reply timestamp         │
│ bounced_at      │ TIMESTAMP       │ Bounce timestamp        │
│ bounce_type     │ ENUM            │ hard/soft bounce        │
│ status          │ ENUM            │ Email status            │
│ contact_id      │ UUID (FK)       │ Related contact         │
│ lead_id         │ UUID (FK)       │ Related lead            │
│ opportunity_id  │ UUID (FK)       │ Related opportunity     │
│ user_id         │ UUID (FK)       │ Sending user            │
│ sequence_id     │ UUID (FK)       │ Email sequence          │
│ sequence_step   │ INTEGER         │ Step in sequence        │
│ organization_id │ UUID (FK)       │ Parent organization     │
│ created_at      │ TIMESTAMP       │ Creation timestamp      │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (organization_id, contact_id)                       │
│ • INDEX (user_id, sent_at)                                  │
│ • INDEX (message_id)                                        │
│ • INDEX (sequence_id, sequence_step)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI & Analytics

### LeadScore

AI-generated lead scores and insights.

```
┌─────────────────────────────────────────────────────────────┐
│                      LeadScore                               │
├─────────────────────────────────────────────────────────────┤
│ id              │ UUID (PK)       │ Unique identifier       │
│ lead_id         │ UUID (FK)       │ Scored lead             │
│ score           │ INTEGER         │ Overall score (0-100)   │
│ grade           │ CHAR(1)         │ Letter grade (A-F)      │
│ breakdown       │ JSONB           │ Score component details │
│ factors         │ JSONB           │ Contributing factors    │
│ recommendation  │ TEXT            │ AI recommendation       │
│ confidence      │ DECIMAL(3,2)    │ Score confidence        │
│ model_version   │ VARCHAR(50)     │ Scoring model version   │
│ scored_at       │ TIMESTAMP       │ Scoring timestamp       │
│ expires_at      │ TIMESTAMP       │ Score expiry            │
│ organization_id │ UUID (FK)       │ Parent organization     │
├─────────────────────────────────────────────────────────────┤
│ INDEXES                                                      │
│ • PRIMARY KEY (id)                                          │
│ • INDEX (lead_id, scored_at DESC)                           │
│ • INDEX (organization_id, score DESC)                       │
└─────────────────────────────────────────────────────────────┘

Breakdown Structure:
{
  "engagement": 25,    // Email opens, clicks, meetings
  "fit": 30,          // Company size, industry match
  "intent": 20,       // Website visits, content downloads
  "timing": 15,       // Recency, velocity
  "budget": 10        // Budget indicators
}
```

---

## 📊 Entity Relationship Diagram

```
                                    ┌──────────────┐
                                    │ Organization │
                                    └──────┬───────┘
                                           │
           ┌───────────────────────────────┼───────────────────────────────┐
           │                               │                               │
    ┌──────▼──────┐                 ┌──────▼──────┐                ┌──────▼──────┐
    │    User     │                 │   Company   │                │  Pipeline   │
    └──────┬──────┘                 └──────┬──────┘                └──────┬──────┘
           │                               │                               │
    ┌──────┼──────┐                        │                        ┌──────▼──────┐
    │      │      │                        │                        │    Stage    │
    │      │      │                        │                        └──────┬──────┘
    ▼      ▼      ▼                        │                               │
┌──────┐┌──────┐┌──────┐                   │                               │
│Contact││ Lead ││ Task │                   │                               │
└──┬───┘└──┬───┘└──────┘                   │                               │
   │       │                                │                               │
   │       └──────────────┬────────────────┼───────────────────────────────┤
   │                      │                │                               │
   │                      ▼                ▼                               ▼
   │               ┌─────────────────────────────┐
   └──────────────▶│       Opportunity           │
                   └─────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  Activity   │    │  LineItem   │    │   Note      │
    └─────────────┘    └─────────────┘    └─────────────┘
```

---

*Last Updated: December 2024*
*Schema Version: 2.0.0*
