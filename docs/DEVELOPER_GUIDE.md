# 👨‍💻 MyCRM Developer Guide

## Welcome to MyCRM Development

This guide provides everything you need to set up your development environment, understand the codebase, and contribute to MyCRM.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Git Workflow](#git-workflow)
7. [Debugging Tips](#debugging-tips)
8. [Performance Guidelines](#performance-guidelines)

---

## 🔧 Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.11+ | [python.org](https://python.org) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org) |
| **Docker** | 24+ | [docker.com](https://docker.com) |
| **Git** | 2.40+ | [git-scm.com](https://git-scm.com) |
| **Flutter** | 3.8+ | [flutter.dev](https://flutter.dev) |

### Recommended Tools

| Tool | Purpose |
|------|---------|
| **VS Code** | Primary IDE |
| **PyCharm** | Python development |
| **Postman** | API testing |
| **TablePlus** | Database management |
| **Redis Insight** | Redis debugging |

### VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "dart-code.flutter",
    "ms-azuretools.vscode-docker",
    "eamodio.gitlens",
    "usernamehw.errorlens",
    "formulahendry.auto-rename-tag"
  ]
}
```

---

## 🚀 Development Setup

### Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/your-org/mycrm.git
cd mycrm

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Access services:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env

# Edit .env with your settings
# Required: DATABASE_URL, SECRET_KEY, REDIS_URL

# Run database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json

# Start development server
python manage.py runserver
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

#### Mobile App Setup

```bash
cd flutter_part

# Get dependencies
flutter pub get

# Run on device/emulator
flutter run

# Run on specific platform
flutter run -d chrome  # Web
flutter run -d ios     # iOS Simulator
flutter run -d android # Android Emulator
```

### Environment Variables

#### Backend (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/mycrm

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-key

# AI/ML
OPENAI_API_KEY=sk-your-openai-key

# Security
ENCRYPTION_KEY=your-encryption-key
JWT_SECRET_KEY=your-jwt-secret

# Feature Flags
ENABLE_AI_FEATURES=True
ENABLE_ENTERPRISE_FEATURES=True
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=MyCRM
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

---

## 📁 Project Structure

### Backend Structure

```
backend/
├── backend/                  # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Base settings
│   ├── settings_production.py # Production overrides
│   ├── urls.py              # Root URL configuration
│   ├── celery.py            # Celery configuration
│   └── asgi.py              # ASGI for WebSockets
│
├── core/                     # Core functionality
│   ├── models.py            # Base models, mixins
│   ├── permissions.py       # Custom permissions
│   ├── pagination.py        # Custom pagination
│   ├── exceptions.py        # Custom exceptions
│   ├── middleware.py        # Custom middleware
│   └── utils/               # Utility functions
│       ├── encryption.py
│       ├── validators.py
│       └── helpers.py
│
├── user_management/          # User & authentication
│   ├── models.py            # User model
│   ├── serializers.py       # User serializers
│   ├── views.py             # Auth views
│   └── permissions.py       # Role permissions
│
├── contact_management/       # Contact module
│   ├── models.py            # Contact, ContactGroup
│   ├── serializers.py
│   ├── views.py             # ContactViewSet
│   ├── filters.py           # Contact filters
│   └── services.py          # Business logic
│
├── lead_management/          # Lead module
│   ├── models.py            # Lead, LeadActivity
│   ├── serializers.py
│   ├── views.py
│   ├── scoring.py           # Lead scoring engine
│   └── services.py
│
├── opportunity_management/   # Opportunity module
│   ├── models.py            # Opportunity, Stage
│   ├── serializers.py
│   ├── views.py
│   └── services.py
│
├── task_management/          # Task module
│   ├── models.py            # Task, Reminder
│   ├── serializers.py
│   ├── views.py
│   └── signals.py           # Task notifications
│
├── ai_insights/              # AI features
│   ├── models.py
│   ├── services/
│   │   ├── scoring.py       # ML scoring
│   │   ├── assistant.py     # AI assistant
│   │   └── predictions.py   # Churn/forecast
│   └── tasks.py             # Async AI tasks
│
├── api/                      # API configuration
│   ├── v1/                  # API version 1
│   │   ├── urls.py
│   │   └── views.py
│   └── schemas.py           # OpenAPI schemas
│
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── factories.py         # Test factories
│   ├── test_contacts.py
│   ├── test_leads.py
│   └── test_api.py
│
└── manage.py
```

### Frontend Structure

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   ├── login/           # Auth pages
│   │   ├── dashboard/       # Dashboard
│   │   ├── contacts/        # Contact pages
│   │   ├── leads/           # Lead pages
│   │   ├── opportunities/   # Opportunity pages
│   │   └── settings/        # Settings pages
│   │
│   ├── components/           # React components
│   │   ├── ui/              # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── layout/          # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── footer.tsx
│   │   ├── contacts/        # Contact components
│   │   ├── leads/           # Lead components
│   │   └── shared/          # Shared components
│   │
│   ├── hooks/                # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useDebounce.ts
│   │
│   ├── lib/                  # Utilities
│   │   ├── api.ts           # API client
│   │   ├── utils.ts         # Helpers
│   │   └── validations.ts   # Form validations
│   │
│   ├── contexts/             # React contexts
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   │
│   └── types/                # TypeScript types
│       ├── api.ts
│       └── models.ts
│
├── public/                   # Static assets
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Mobile App Structure

```
flutter_part/lib/
├── main.dart                 # App entry point
│
├── core/                     # Core infrastructure
│   ├── constants/           # App constants
│   ├── theme/               # Theme configuration
│   └── utils/               # Utilities
│
├── models/                   # Data models
│   ├── user_model.dart
│   ├── contact_model.dart
│   └── lead_model.dart
│
├── providers/                # State management
│   ├── auth_provider.dart
│   ├── contacts_provider.dart
│   └── leads_provider.dart
│
├── services/                 # API services
│   ├── api_service.dart
│   ├── auth_service.dart
│   └── contacts_service.dart
│
├── screens/                  # UI screens
│   ├── auth/
│   ├── home/
│   ├── contacts/
│   └── leads/
│
└── widgets/                  # Reusable widgets
    ├── common/
    └── forms/
```

---

## 📏 Coding Standards

### Python (Backend)

We follow PEP 8 with additional conventions:

```python
# Use type hints
def get_contact_by_email(email: str) -> Contact | None:
    """
    Retrieve a contact by email address.
    
    Args:
        email: The email address to search for.
        
    Returns:
        Contact instance if found, None otherwise.
    """
    return Contact.objects.filter(email=email).first()

# Use dataclasses or Pydantic for data structures
from dataclasses import dataclass

@dataclass
class LeadScoreResult:
    score: int
    breakdown: dict[str, int]
    recommendation: str

# Service layer pattern
class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository
    
    def create_contact(self, data: dict) -> Contact:
        # Validation
        self._validate_email(data['email'])
        
        # Business logic
        contact = self.repository.create(data)
        
        # Side effects
        self._send_welcome_email(contact)
        
        return contact
```

#### Django Best Practices

```python
# ViewSet structure
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ContactFilter
    search_fields = ['first_name', 'last_name', 'email', 'company']
    ordering_fields = ['created_at', 'updated_at', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter contacts by organization for multi-tenancy."""
        return super().get_queryset().filter(
            organization=self.request.user.organization
        ).select_related('owner', 'assigned_to')
    
    @action(detail=True, methods=['post'])
    def merge(self, request, pk=None):
        """Merge duplicate contacts."""
        contact = self.get_object()
        target_id = request.data.get('target_id')
        ContactService.merge_contacts(contact.id, target_id)
        return Response({'status': 'merged'})
```

### TypeScript (Frontend)

```typescript
// Use interfaces for data shapes
interface Contact {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  company?: string;
  tags: string[];
  createdAt: string;
}

// Use type for unions/intersections
type ContactStatus = 'active' | 'inactive' | 'archived';

// Component structure
interface ContactCardProps {
  contact: Contact;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export function ContactCard({ contact, onEdit, onDelete }: ContactCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  
  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(contact.id);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{contact.firstName} {contact.lastName}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{contact.email}</p>
      </CardContent>
      <CardFooter>
        <Button onClick={() => onEdit(contact.id)}>Edit</Button>
        <Button variant="destructive" onClick={handleDelete} disabled={isLoading}>
          Delete
        </Button>
      </CardFooter>
    </Card>
  );
}
```

### Dart (Flutter)

```dart
// Model with freezed
import 'package:freezed_annotation/freezed_annotation.dart';

part 'contact_model.freezed.dart';
part 'contact_model.g.dart';

@freezed
class Contact with _$Contact {
  const factory Contact({
    required int id,
    required String firstName,
    required String lastName,
    required String email,
    String? company,
    @Default([]) List<String> tags,
  }) = _Contact;
  
  factory Contact.fromJson(Map<String, dynamic> json) => _$ContactFromJson(json);
}

// Provider with Riverpod
@riverpod
class ContactsNotifier extends _$ContactsNotifier {
  @override
  Future<List<Contact>> build() async {
    return ref.read(contactServiceProvider).getContacts();
  }
  
  Future<void> addContact(Contact contact) async {
    await ref.read(contactServiceProvider).createContact(contact);
    ref.invalidateSelf();
  }
}
```

---

## 🧪 Testing Guidelines

### Backend Testing

```python
# tests/test_contacts.py
import pytest
from django.urls import reverse
from rest_framework import status
from .factories import ContactFactory, UserFactory

@pytest.mark.django_db
class TestContactAPI:
    def test_list_contacts(self, api_client, user):
        """Test listing contacts returns paginated results."""
        ContactFactory.create_batch(5, organization=user.organization)
        
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse('contact-list'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5
        assert len(response.data['results']) == 5
    
    def test_create_contact_validates_email(self, api_client, user):
        """Test contact creation validates email format."""
        api_client.force_authenticate(user=user)
        response = api_client.post(reverse('contact-list'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_contact_isolation_by_organization(self, api_client, user):
        """Test users can only see their organization's contacts."""
        # Create contact in different organization
        other_contact = ContactFactory()
        own_contact = ContactFactory(organization=user.organization)
        
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse('contact-list'))
        
        contact_ids = [c['id'] for c in response.data['results']]
        assert own_contact.id in contact_ids
        assert other_contact.id not in contact_ids

# tests/factories.py
import factory
from user_management.models import User
from contact_management.models import Contact

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: f'contact{n}@example.com')
    organization = factory.SubFactory('tests.factories.OrganizationFactory')
```

### Frontend Testing

```typescript
// __tests__/ContactCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ContactCard } from '@/components/contacts/ContactCard';

const mockContact = {
  id: 1,
  firstName: 'John',
  lastName: 'Doe',
  email: 'john@example.com',
  tags: [],
  createdAt: '2024-01-01',
};

describe('ContactCard', () => {
  it('renders contact information', () => {
    render(
      <ContactCard 
        contact={mockContact} 
        onEdit={jest.fn()} 
        onDelete={jest.fn()} 
      />
    );
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
  
  it('calls onEdit when edit button clicked', () => {
    const onEdit = jest.fn();
    render(
      <ContactCard 
        contact={mockContact} 
        onEdit={onEdit} 
        onDelete={jest.fn()} 
      />
    );
    
    fireEvent.click(screen.getByText('Edit'));
    expect(onEdit).toHaveBeenCalledWith(1);
  });
});
```

### Running Tests

```bash
# Backend tests
cd backend
pytest                          # Run all tests
pytest -x                       # Stop on first failure
pytest -v                       # Verbose output
pytest --cov=.                  # With coverage
pytest tests/test_contacts.py   # Specific file
pytest -k "test_create"         # By name pattern

# Frontend tests
cd frontend
npm test                        # Run all tests
npm test -- --watch             # Watch mode
npm test -- --coverage          # With coverage

# Flutter tests
cd flutter_part
flutter test                    # Run all tests
flutter test --coverage         # With coverage
```

---

## 🔀 Git Workflow

### Branch Naming

```
feature/CRM-123-add-lead-scoring
bugfix/CRM-456-fix-contact-export
hotfix/CRM-789-security-patch
chore/update-dependencies
docs/api-documentation
```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(leads): add AI-powered lead scoring

- Implement ML model for lead scoring
- Add scoring breakdown API endpoint
- Create background task for batch scoring

Closes #123
```

```
fix(contacts): resolve duplicate detection issue

The duplicate detection was matching on partial email
addresses. Now requires exact match.

Fixes #456
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes with atomic commits
3. Write/update tests
4. Update documentation
5. Create PR with description template
6. Address review feedback
7. Squash and merge

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

---

## 🐛 Debugging Tips

### Backend Debugging

```python
# Django Debug Toolbar (development only)
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# IPython for interactive debugging
# pip install ipdb
import ipdb; ipdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug('Debug message with data: %s', data)

# SQL query logging
LOGGING = {
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

### Frontend Debugging

```typescript
// React Query DevTools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// In app layout
<ReactQueryDevtools initialIsOpen={false} />

// Console debugging
console.log('State:', state);
console.table(contacts);
console.time('operation');
// ... operation
console.timeEnd('operation');

// React Developer Tools browser extension
```

### Celery Debugging

```bash
# Start Celery with verbose logging
celery -A backend worker -l DEBUG

# Monitor tasks
celery -A backend flower

# Inspect active tasks
celery -A backend inspect active
```

---

## ⚡ Performance Guidelines

### Backend Performance

```python
# Use select_related for foreign keys
Contact.objects.select_related('owner', 'organization')

# Use prefetch_related for many-to-many
Lead.objects.prefetch_related('tags', 'activities')

# Avoid N+1 queries
# Bad:
for contact in contacts:
    print(contact.owner.name)  # N queries

# Good:
for contact in Contact.objects.select_related('owner'):
    print(contact.owner.name)  # 1 query

# Use only/defer for partial loading
Contact.objects.only('id', 'email', 'first_name')

# Bulk operations
Contact.objects.bulk_create([...])
Contact.objects.bulk_update([...], ['status'])

# Use indexes
class Contact(models.Model):
    email = models.EmailField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['created_at']),
        ]
```

### Frontend Performance

```typescript
// Memoize expensive computations
const sortedContacts = useMemo(() => {
  return [...contacts].sort((a, b) => a.lastName.localeCompare(b.lastName));
}, [contacts]);

// Debounce search input
const debouncedSearch = useDebouncedCallback((value: string) => {
  setSearchQuery(value);
}, 300);

// Virtual scrolling for long lists
import { useVirtualizer } from '@tanstack/react-virtual';

// Lazy load components
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
});

// Image optimization
import Image from 'next/image';
<Image src={avatar} width={40} height={40} alt="Avatar" />
```

---

## 🆘 Getting Help

- **Documentation:** [docs/](./docs/)
- **GitHub Issues:** Report bugs and request features
- **Discord:** Join our developer community
- **Stack Overflow:** Tag questions with `mycrm`

---

*Last Updated: December 2024*
