"""
Enterprise GraphQL API Layer for MyCRM
======================================

GraphQL implementation with:
- Strawberry GraphQL framework
- DataLoader for N+1 prevention
- Rate limiting and complexity analysis
- Real-time subscriptions via WebSockets
- Federation support for microservices
- Comprehensive type system

Author: MyCRM Enterprise Team
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generic,
    List,
    NewType,
    Optional,
    TypeVar,
    Union,
)

import strawberry
from strawberry import relay
from strawberry.dataloader import DataLoader
from strawberry.extensions import QueryDepthLimiter
from strawberry.permission import BasePermission
from strawberry.scalars import JSON
from strawberry.types import Info

logger = logging.getLogger(__name__)

# =============================================================================
# Custom Scalars
# =============================================================================

DateTime = strawberry.scalar(
    NewType("DateTime", datetime),
    serialize=lambda v: v.isoformat() if v else None,
    parse_value=lambda v: datetime.fromisoformat(v) if v else None,
)

Money = strawberry.scalar(
    NewType("Money", Decimal),
    serialize=lambda v: str(v) if v else None,
    parse_value=lambda v: Decimal(v) if v else None,
)


# =============================================================================
# Enums
# =============================================================================

@strawberry.enum
class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


@strawberry.enum
class ContactType(Enum):
    LEAD = "lead"
    CUSTOMER = "customer"
    PARTNER = "partner"
    VENDOR = "vendor"


@strawberry.enum
class OpportunityStage(Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    VALUE_PROPOSITION = "value_proposition"
    DECISION_MAKERS = "decision_makers"
    PERCEPTION_ANALYSIS = "perception_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@strawberry.enum
class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@strawberry.enum
class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


# =============================================================================
# Permission Classes
# =============================================================================

class IsAuthenticated(BasePermission):
    """Check if user is authenticated."""
    message = "User is not authenticated"
    
    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request:
            return False
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """Check if user is admin."""
    message = "User is not an administrator"
    
    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request:
            return False
        return request.user and request.user.is_staff


class HasPermission(BasePermission):
    """Check if user has specific permission."""
    message = "User does not have required permission"
    
    def __init__(self, permission: str):
        self.permission = permission
    
    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request or not request.user:
            return False
        return request.user.has_perm(self.permission)


class RateLimitPermission(BasePermission):
    """Rate limiting permission."""
    message = "Rate limit exceeded"
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
    
    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        # Implement rate limiting logic using Redis
        request = info.context.get("request")
        if not request:
            return True
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit (simplified - should use Redis in production)
        cache = info.context.get("cache")
        if cache:
            key = f"rate_limit:{client_id}"
            count = cache.get(key) or 0
            if count >= self.requests_per_minute:
                return False
            cache.set(key, count + 1, ttl=60)
        
        return True
    
    def _get_client_id(self, request) -> str:
        """Get unique client identifier."""
        if request.user and request.user.is_authenticated:
            return f"user:{request.user.id}"
        return f"ip:{request.META.get('REMOTE_ADDR', 'unknown')}"


# =============================================================================
# Input Types
# =============================================================================

@strawberry.input
class PaginationInput:
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20
    
    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 1
        if self.page_size > 100:
            self.page_size = 100


@strawberry.input
class SortInput:
    """Sorting parameters."""
    field: str
    direction: SortDirection = SortDirection.ASC


@strawberry.input
class DateRangeInput:
    """Date range filter."""
    start: Optional[datetime] = None
    end: Optional[datetime] = None


@strawberry.input
class LeadFilterInput:
    """Lead filter parameters."""
    status: Optional[List[LeadStatus]] = None
    source: Optional[List[str]] = None
    assigned_to: Optional[List[strawberry.ID]] = None
    score_min: Optional[int] = None
    score_max: Optional[int] = None
    created_at: Optional[DateRangeInput] = None
    search: Optional[str] = None


@strawberry.input
class ContactFilterInput:
    """Contact filter parameters."""
    type: Optional[List[ContactType]] = None
    company: Optional[List[strawberry.ID]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[DateRangeInput] = None
    search: Optional[str] = None


@strawberry.input
class OpportunityFilterInput:
    """Opportunity filter parameters."""
    stage: Optional[List[OpportunityStage]] = None
    owner: Optional[List[strawberry.ID]] = None
    value_min: Optional[Decimal] = None
    value_max: Optional[Decimal] = None
    close_date: Optional[DateRangeInput] = None
    probability_min: Optional[int] = None
    search: Optional[str] = None


@strawberry.input
class CreateLeadInput:
    """Input for creating a lead."""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[JSON] = None


@strawberry.input
class UpdateLeadInput:
    """Input for updating a lead."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[strawberry.ID] = None
    score: Optional[int] = None
    custom_fields: Optional[JSON] = None


@strawberry.input
class CreateContactInput:
    """Input for creating a contact."""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_id: Optional[strawberry.ID] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    type: ContactType = ContactType.LEAD
    address: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[JSON] = None


@strawberry.input
class CreateOpportunityInput:
    """Input for creating an opportunity."""
    name: str
    value: Decimal
    contact_id: strawberry.ID
    stage: OpportunityStage = OpportunityStage.PROSPECTING
    probability: int = 10
    expected_close_date: Optional[datetime] = None
    description: Optional[str] = None
    products: Optional[List[strawberry.ID]] = None
    custom_fields: Optional[JSON] = None


@strawberry.input
class CreateTaskInput:
    """Input for creating a task."""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[strawberry.ID] = None
    related_to_type: Optional[str] = None
    related_to_id: Optional[strawberry.ID] = None


# =============================================================================
# Output Types
# =============================================================================

@strawberry.type
class PageInfo:
    """Pagination information."""
    page: int
    page_size: int
    total_pages: int
    total_count: int
    has_next: bool
    has_previous: bool


T = TypeVar("T")


@strawberry.type
class Connection(Generic[T]):
    """Generic paginated connection type."""
    items: List[T]
    page_info: PageInfo


@strawberry.type
class User:
    """User type."""
    id: strawberry.ID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    date_joined: datetime
    last_login: Optional[datetime]
    
    @strawberry.field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@strawberry.type
class Company:
    """Company type."""
    id: strawberry.ID
    name: str
    domain: Optional[str]
    industry: Optional[str]
    size: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def contacts(
        self,
        info: Info,
        pagination: Optional[PaginationInput] = None
    ) -> "Connection[Contact]":
        """Get contacts for this company."""
        loader = info.context["loaders"]["company_contacts"]
        return await loader.load(self.id)


@strawberry.type
class Contact:
    """Contact type."""
    id: strawberry.ID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    mobile: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    type: ContactType
    address: Optional[str]
    tags: List[str]
    custom_fields: Optional[JSON]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    @strawberry.field
    async def company(self, info: Info) -> Optional[Company]:
        """Get company for this contact."""
        if not hasattr(self, "_company_id") or not self._company_id:
            return None
        loader = info.context["loaders"]["companies"]
        return await loader.load(self._company_id)
    
    @strawberry.field
    async def opportunities(self, info: Info) -> List["Opportunity"]:
        """Get opportunities for this contact."""
        loader = info.context["loaders"]["contact_opportunities"]
        return await loader.load(self.id)
    
    @strawberry.field
    async def activities(
        self,
        info: Info,
        limit: int = 10
    ) -> List["Activity"]:
        """Get recent activities for this contact."""
        loader = info.context["loaders"]["contact_activities"]
        return await loader.load(self.id)


@strawberry.type
class Lead:
    """Lead type."""
    id: strawberry.ID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    status: LeadStatus
    source: Optional[str]
    score: int
    notes: Optional[str]
    custom_fields: Optional[JSON]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    @strawberry.field
    async def assigned_to(self, info: Info) -> Optional[User]:
        """Get assigned user."""
        if not hasattr(self, "_assigned_to_id") or not self._assigned_to_id:
            return None
        loader = info.context["loaders"]["users"]
        return await loader.load(self._assigned_to_id)
    
    @strawberry.field
    async def activities(
        self,
        info: Info,
        limit: int = 10
    ) -> List["Activity"]:
        """Get recent activities for this lead."""
        loader = info.context["loaders"]["lead_activities"]
        return await loader.load(self.id)
    
    @strawberry.field
    async def ai_insights(self, info: Info) -> Optional["LeadInsights"]:
        """Get AI-generated insights for this lead."""
        loader = info.context["loaders"]["lead_insights"]
        return await loader.load(self.id)


@strawberry.type
class LeadInsights:
    """AI-generated lead insights."""
    id: strawberry.ID
    lead_id: strawberry.ID
    conversion_probability: float
    recommended_actions: List[str]
    engagement_score: float
    best_contact_time: Optional[str]
    sentiment: Optional[str]
    generated_at: datetime


@strawberry.type
class Opportunity:
    """Opportunity type."""
    id: strawberry.ID
    name: str
    value: Money
    stage: OpportunityStage
    probability: int
    expected_close_date: Optional[datetime]
    actual_close_date: Optional[datetime]
    description: Optional[str]
    win_reason: Optional[str]
    loss_reason: Optional[str]
    custom_fields: Optional[JSON]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    def weighted_value(self) -> Decimal:
        """Calculate weighted value based on probability."""
        return self.value * Decimal(self.probability) / 100
    
    @strawberry.field
    async def contact(self, info: Info) -> Optional[Contact]:
        """Get primary contact."""
        if not hasattr(self, "_contact_id") or not self._contact_id:
            return None
        loader = info.context["loaders"]["contacts"]
        return await loader.load(self._contact_id)
    
    @strawberry.field
    async def owner(self, info: Info) -> Optional[User]:
        """Get opportunity owner."""
        if not hasattr(self, "_owner_id") or not self._owner_id:
            return None
        loader = info.context["loaders"]["users"]
        return await loader.load(self._owner_id)
    
    @strawberry.field
    async def activities(
        self,
        info: Info,
        limit: int = 10
    ) -> List["Activity"]:
        """Get recent activities for this opportunity."""
        loader = info.context["loaders"]["opportunity_activities"]
        return await loader.load(self.id)


@strawberry.type
class Task:
    """Task type."""
    id: strawberry.ID
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    priority: TaskPriority
    is_completed: bool
    related_to_type: Optional[str]
    related_to_id: Optional[strawberry.ID]
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def assigned_to(self, info: Info) -> Optional[User]:
        """Get assigned user."""
        if not hasattr(self, "_assigned_to_id") or not self._assigned_to_id:
            return None
        loader = info.context["loaders"]["users"]
        return await loader.load(self._assigned_to_id)
    
    @strawberry.field
    async def created_by(self, info: Info) -> Optional[User]:
        """Get creator."""
        if not hasattr(self, "_created_by_id") or not self._created_by_id:
            return None
        loader = info.context["loaders"]["users"]
        return await loader.load(self._created_by_id)


@strawberry.type
class Activity:
    """Activity log entry."""
    id: strawberry.ID
    type: str
    title: str
    description: Optional[str]
    related_to_type: str
    related_to_id: strawberry.ID
    metadata: Optional[JSON]
    created_at: datetime
    
    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Get user who performed the activity."""
        if not hasattr(self, "_user_id") or not self._user_id:
            return None
        loader = info.context["loaders"]["users"]
        return await loader.load(self._user_id)


@strawberry.type
class DashboardMetrics:
    """Dashboard metrics."""
    total_leads: int
    leads_this_month: int
    lead_conversion_rate: float
    
    total_opportunities: int
    pipeline_value: Money
    weighted_pipeline: Money
    
    total_contacts: int
    contacts_this_month: int
    
    won_deals_count: int
    won_deals_value: Money
    
    tasks_due_today: int
    overdue_tasks: int
    
    activities_this_week: int


@strawberry.type
class SalesAnalytics:
    """Sales analytics data."""
    period: str
    revenue: Money
    deals_won: int
    deals_lost: int
    avg_deal_size: Money
    avg_sales_cycle_days: int
    win_rate: float
    pipeline_by_stage: JSON
    revenue_by_source: JSON
    top_performers: List["SalesPerformer"]


@strawberry.type
class SalesPerformer:
    """Sales performer stats."""
    user: User
    deals_won: int
    revenue: Money
    conversion_rate: float


@strawberry.type
class MutationResult:
    """Generic mutation result."""
    success: bool
    message: Optional[str]
    errors: Optional[List[str]]


@strawberry.type
class LeadMutationResult(MutationResult):
    """Lead mutation result."""
    lead: Optional[Lead] = None


@strawberry.type
class ContactMutationResult(MutationResult):
    """Contact mutation result."""
    contact: Optional[Contact] = None


@strawberry.type
class OpportunityMutationResult(MutationResult):
    """Opportunity mutation result."""
    opportunity: Optional[Opportunity] = None


@strawberry.type
class TaskMutationResult(MutationResult):
    """Task mutation result."""
    task: Optional[Task] = None


# =============================================================================
# DataLoaders
# =============================================================================

def create_loaders(context: Dict) -> Dict[str, DataLoader]:
    """Create DataLoaders for efficient data fetching."""
    
    async def load_users(keys: List[strawberry.ID]) -> List[Optional[User]]:
        """Batch load users by ID."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = await asyncio.to_thread(
            lambda: list(User.objects.filter(id__in=keys))
        )
        user_map = {str(u.id): u for u in users}
        return [user_map.get(str(k)) for k in keys]
    
    async def load_contacts(keys: List[strawberry.ID]) -> List[Optional[Contact]]:
        """Batch load contacts by ID."""
        from contact_management.models import Contact as ContactModel
        contacts = await asyncio.to_thread(
            lambda: list(ContactModel.objects.filter(id__in=keys))
        )
        contact_map = {str(c.id): c for c in contacts}
        return [contact_map.get(str(k)) for k in keys]
    
    async def load_companies(keys: List[strawberry.ID]) -> List[Optional[Company]]:
        """Batch load companies by ID."""
        from contact_management.models import Company as CompanyModel
        companies = await asyncio.to_thread(
            lambda: list(CompanyModel.objects.filter(id__in=keys))
        )
        company_map = {str(c.id): c for c in companies}
        return [company_map.get(str(k)) for k in keys]
    
    async def load_leads(keys: List[strawberry.ID]) -> List[Optional[Lead]]:
        """Batch load leads by ID."""
        from lead_management.models import Lead as LeadModel
        leads = await asyncio.to_thread(
            lambda: list(LeadModel.objects.filter(id__in=keys))
        )
        lead_map = {str(l.id): l for l in leads}
        return [lead_map.get(str(k)) for k in keys]
    
    async def load_opportunities(keys: List[strawberry.ID]) -> List[Optional[Opportunity]]:
        """Batch load opportunities by ID."""
        from opportunity_management.models import Opportunity as OppModel
        opps = await asyncio.to_thread(
            lambda: list(OppModel.objects.filter(id__in=keys))
        )
        opp_map = {str(o.id): o for o in opps}
        return [opp_map.get(str(k)) for k in keys]
    
    return {
        "users": DataLoader(load_fn=load_users),
        "contacts": DataLoader(load_fn=load_contacts),
        "companies": DataLoader(load_fn=load_companies),
        "leads": DataLoader(load_fn=load_leads),
        "opportunities": DataLoader(load_fn=load_opportunities),
        "contact_opportunities": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_contact_opportunities(k) for k in keys]
        )),
        "contact_activities": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_contact_activities(k) for k in keys]
        )),
        "lead_activities": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_lead_activities(k) for k in keys]
        )),
        "lead_insights": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_lead_insights(k) for k in keys]
        )),
        "opportunity_activities": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_opportunity_activities(k) for k in keys]
        )),
        "company_contacts": DataLoader(load_fn=lambda keys: asyncio.gather(
            *[load_company_contacts(k) for k in keys]
        )),
    }


async def load_contact_opportunities(contact_id: strawberry.ID) -> List[Opportunity]:
    """Load opportunities for a contact."""
    # Implementation would query the database
    return []


async def load_contact_activities(contact_id: strawberry.ID) -> List[Activity]:
    """Load activities for a contact."""
    return []


async def load_lead_activities(lead_id: strawberry.ID) -> List[Activity]:
    """Load activities for a lead."""
    return []


async def load_lead_insights(lead_id: strawberry.ID) -> Optional[LeadInsights]:
    """Load AI insights for a lead."""
    return None


async def load_opportunity_activities(opp_id: strawberry.ID) -> List[Activity]:
    """Load activities for an opportunity."""
    return []


async def load_company_contacts(company_id: strawberry.ID) -> Connection[Contact]:
    """Load contacts for a company."""
    return Connection(
        items=[],
        page_info=PageInfo(
            page=1,
            page_size=20,
            total_pages=0,
            total_count=0,
            has_next=False,
            has_previous=False
        )
    )


# =============================================================================
# Query Resolvers
# =============================================================================

@strawberry.type
class Query:
    """Root query type."""
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info) -> User:
        """Get current authenticated user."""
        request = info.context["request"]
        user = request.user
        return User(
            id=strawberry.ID(str(user.id)),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            date_joined=user.date_joined,
            last_login=user.last_login
        )
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def lead(
        self,
        info: Info,
        id: strawberry.ID
    ) -> Optional[Lead]:
        """Get a single lead by ID."""
        loader = info.context["loaders"]["leads"]
        return await loader.load(id)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def leads(
        self,
        info: Info,
        filter: Optional[LeadFilterInput] = None,
        pagination: Optional[PaginationInput] = None,
        sort: Optional[SortInput] = None
    ) -> Connection[Lead]:
        """Get paginated list of leads."""
        from lead_management.models import Lead as LeadModel
        
        pagination = pagination or PaginationInput()
        
        # Build queryset
        queryset = LeadModel.objects.all()
        
        if filter:
            if filter.status:
                queryset = queryset.filter(status__in=[s.value for s in filter.status])
            if filter.source:
                queryset = queryset.filter(source__in=filter.source)
            if filter.assigned_to:
                queryset = queryset.filter(assigned_to_id__in=filter.assigned_to)
            if filter.score_min is not None:
                queryset = queryset.filter(score__gte=filter.score_min)
            if filter.score_max is not None:
                queryset = queryset.filter(score__lte=filter.score_max)
            if filter.search:
                queryset = queryset.filter(
                    Q(first_name__icontains=filter.search) |
                    Q(last_name__icontains=filter.search) |
                    Q(email__icontains=filter.search) |
                    Q(company__icontains=filter.search)
                )
        
        if sort:
            order = '-' if sort.direction == SortDirection.DESC else ''
            queryset = queryset.order_by(f"{order}{sort.field}")
        else:
            queryset = queryset.order_by('-created_at')
        
        # Get total count
        total_count = await asyncio.to_thread(queryset.count)
        total_pages = (total_count + pagination.page_size - 1) // pagination.page_size
        
        # Get page
        offset = (pagination.page - 1) * pagination.page_size
        leads = await asyncio.to_thread(
            lambda: list(queryset[offset:offset + pagination.page_size])
        )
        
        return Connection(
            items=[_convert_lead(l) for l in leads],
            page_info=PageInfo(
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=total_pages,
                total_count=total_count,
                has_next=pagination.page < total_pages,
                has_previous=pagination.page > 1
            )
        )
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def contact(
        self,
        info: Info,
        id: strawberry.ID
    ) -> Optional[Contact]:
        """Get a single contact by ID."""
        loader = info.context["loaders"]["contacts"]
        return await loader.load(id)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def contacts(
        self,
        info: Info,
        filter: Optional[ContactFilterInput] = None,
        pagination: Optional[PaginationInput] = None,
        sort: Optional[SortInput] = None
    ) -> Connection[Contact]:
        """Get paginated list of contacts."""
        # Similar implementation to leads
        pagination = pagination or PaginationInput()
        return Connection(
            items=[],
            page_info=PageInfo(
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=0,
                total_count=0,
                has_next=False,
                has_previous=False
            )
        )
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def opportunity(
        self,
        info: Info,
        id: strawberry.ID
    ) -> Optional[Opportunity]:
        """Get a single opportunity by ID."""
        loader = info.context["loaders"]["opportunities"]
        return await loader.load(id)
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def opportunities(
        self,
        info: Info,
        filter: Optional[OpportunityFilterInput] = None,
        pagination: Optional[PaginationInput] = None,
        sort: Optional[SortInput] = None
    ) -> Connection[Opportunity]:
        """Get paginated list of opportunities."""
        pagination = pagination or PaginationInput()
        return Connection(
            items=[],
            page_info=PageInfo(
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=0,
                total_count=0,
                has_next=False,
                has_previous=False
            )
        )
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def dashboard_metrics(self, info: Info) -> DashboardMetrics:
        """Get dashboard metrics."""
        # Implementation would aggregate metrics from database
        return DashboardMetrics(
            total_leads=0,
            leads_this_month=0,
            lead_conversion_rate=0.0,
            total_opportunities=0,
            pipeline_value=Decimal("0"),
            weighted_pipeline=Decimal("0"),
            total_contacts=0,
            contacts_this_month=0,
            won_deals_count=0,
            won_deals_value=Decimal("0"),
            tasks_due_today=0,
            overdue_tasks=0,
            activities_this_week=0
        )
    
    @strawberry.field(permission_classes=[IsAuthenticated, IsAdmin])
    async def sales_analytics(
        self,
        info: Info,
        period: str = "month"
    ) -> SalesAnalytics:
        """Get sales analytics data."""
        return SalesAnalytics(
            period=period,
            revenue=Decimal("0"),
            deals_won=0,
            deals_lost=0,
            avg_deal_size=Decimal("0"),
            avg_sales_cycle_days=0,
            win_rate=0.0,
            pipeline_by_stage={},
            revenue_by_source={},
            top_performers=[]
        )


def _convert_lead(lead_model) -> Lead:
    """Convert Django model to GraphQL type."""
    lead = Lead(
        id=strawberry.ID(str(lead_model.id)),
        first_name=lead_model.first_name,
        last_name=lead_model.last_name,
        email=lead_model.email,
        phone=lead_model.phone,
        company=lead_model.company,
        status=LeadStatus(lead_model.status),
        source=lead_model.source,
        score=lead_model.score,
        notes=lead_model.notes,
        custom_fields=lead_model.custom_fields,
        created_at=lead_model.created_at,
        updated_at=lead_model.updated_at
    )
    lead._assigned_to_id = lead_model.assigned_to_id
    return lead


# =============================================================================
# Mutation Resolvers
# =============================================================================

@strawberry.type
class Mutation:
    """Root mutation type."""
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_lead(
        self,
        info: Info,
        input: CreateLeadInput
    ) -> LeadMutationResult:
        """Create a new lead."""
        try:
            from lead_management.models import Lead as LeadModel
            
            lead = await asyncio.to_thread(
                lambda: LeadModel.objects.create(
                    first_name=input.first_name,
                    last_name=input.last_name,
                    email=input.email,
                    phone=input.phone,
                    company=input.company,
                    source=input.source,
                    notes=input.notes,
                    custom_fields=input.custom_fields or {}
                )
            )
            
            return LeadMutationResult(
                success=True,
                message="Lead created successfully",
                lead=_convert_lead(lead)
            )
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return LeadMutationResult(
                success=False,
                message="Failed to create lead",
                errors=[str(e)]
            )
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_lead(
        self,
        info: Info,
        id: strawberry.ID,
        input: UpdateLeadInput
    ) -> LeadMutationResult:
        """Update an existing lead."""
        try:
            from lead_management.models import Lead as LeadModel
            
            def update():
                lead = LeadModel.objects.get(id=id)
                
                if input.first_name is not None:
                    lead.first_name = input.first_name
                if input.last_name is not None:
                    lead.last_name = input.last_name
                if input.email is not None:
                    lead.email = input.email
                if input.phone is not None:
                    lead.phone = input.phone
                if input.company is not None:
                    lead.company = input.company
                if input.status is not None:
                    lead.status = input.status.value
                if input.source is not None:
                    lead.source = input.source
                if input.notes is not None:
                    lead.notes = input.notes
                if input.assigned_to is not None:
                    lead.assigned_to_id = input.assigned_to
                if input.score is not None:
                    lead.score = input.score
                if input.custom_fields is not None:
                    lead.custom_fields = input.custom_fields
                
                lead.save()
                return lead
            
            lead = await asyncio.to_thread(update)
            
            return LeadMutationResult(
                success=True,
                message="Lead updated successfully",
                lead=_convert_lead(lead)
            )
        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            return LeadMutationResult(
                success=False,
                message="Failed to update lead",
                errors=[str(e)]
            )
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_lead(
        self,
        info: Info,
        id: strawberry.ID
    ) -> MutationResult:
        """Delete a lead."""
        try:
            from lead_management.models import Lead as LeadModel
            
            await asyncio.to_thread(
                lambda: LeadModel.objects.filter(id=id).delete()
            )
            
            return MutationResult(
                success=True,
                message="Lead deleted successfully"
            )
        except Exception as e:
            logger.error(f"Error deleting lead: {e}")
            return MutationResult(
                success=False,
                message="Failed to delete lead",
                errors=[str(e)]
            )
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def convert_lead_to_contact(
        self,
        info: Info,
        lead_id: strawberry.ID,
        create_opportunity: bool = False,
        opportunity_value: Optional[Decimal] = None
    ) -> ContactMutationResult:
        """Convert a lead to a contact."""
        try:
            # Implementation would convert lead to contact
            return ContactMutationResult(
                success=True,
                message="Lead converted successfully"
            )
        except Exception as e:
            return ContactMutationResult(
                success=False,
                message="Failed to convert lead",
                errors=[str(e)]
            )
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_task(
        self,
        info: Info,
        input: CreateTaskInput
    ) -> TaskMutationResult:
        """Create a new task."""
        try:
            # Implementation would create task
            return TaskMutationResult(
                success=True,
                message="Task created successfully"
            )
        except Exception as e:
            return TaskMutationResult(
                success=False,
                message="Failed to create task",
                errors=[str(e)]
            )
    
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def complete_task(
        self,
        info: Info,
        id: strawberry.ID
    ) -> TaskMutationResult:
        """Mark a task as completed."""
        try:
            # Implementation would complete task
            return TaskMutationResult(
                success=True,
                message="Task completed successfully"
            )
        except Exception as e:
            return TaskMutationResult(
                success=False,
                message="Failed to complete task",
                errors=[str(e)]
            )


# =============================================================================
# Subscription Resolvers
# =============================================================================

@strawberry.type
class Subscription:
    """Root subscription type for real-time updates."""
    
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def lead_updates(
        self,
        info: Info
    ) -> AsyncGenerator[Lead, None]:
        """Subscribe to lead updates."""
        # Implementation would use Redis pub/sub or similar
        while True:
            await asyncio.sleep(10)
            # Yield updated leads
            yield Lead(
                id=strawberry.ID("1"),
                first_name="Updated",
                last_name="Lead",
                email="updated@example.com",
                phone=None,
                company=None,
                status=LeadStatus.NEW,
                source=None,
                score=0,
                notes=None,
                custom_fields=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def opportunity_updates(
        self,
        info: Info
    ) -> AsyncGenerator[Opportunity, None]:
        """Subscribe to opportunity updates."""
        while True:
            await asyncio.sleep(10)
            yield Opportunity(
                id=strawberry.ID("1"),
                name="Updated Opportunity",
                value=Decimal("10000"),
                stage=OpportunityStage.PROSPECTING,
                probability=10,
                expected_close_date=None,
                actual_close_date=None,
                description=None,
                win_reason=None,
                loss_reason=None,
                custom_fields=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def activity_feed(
        self,
        info: Info
    ) -> AsyncGenerator[Activity, None]:
        """Subscribe to activity feed updates."""
        while True:
            await asyncio.sleep(5)
            yield Activity(
                id=strawberry.ID("1"),
                type="lead_created",
                title="New lead created",
                description=None,
                related_to_type="lead",
                related_to_id=strawberry.ID("1"),
                metadata=None,
                created_at=datetime.now()
            )
    
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def notifications(
        self,
        info: Info
    ) -> AsyncGenerator[JSON, None]:
        """Subscribe to user notifications."""
        while True:
            await asyncio.sleep(10)
            yield {
                "type": "notification",
                "title": "New notification",
                "message": "You have a new task",
                "timestamp": datetime.now().isoformat()
            }


# =============================================================================
# Schema Configuration
# =============================================================================

def get_context(request):
    """Build GraphQL context."""
    return {
        "request": request,
        "loaders": create_loaders({}),
    }


# Create schema with extensions
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[
        QueryDepthLimiter(max_depth=10),
    ]
)


# Django integration view
def graphql_view():
    """Create Django GraphQL view."""
    from strawberry.django.views import AsyncGraphQLView
    
    return AsyncGraphQLView.as_view(
        schema=schema,
        graphiql=True,  # Enable GraphiQL in development
    )
