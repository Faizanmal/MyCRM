from django.db import models

from .middleware import get_current_organization


class TenantQuerySet(models.QuerySet):
    """
    Custom QuerySet that automatically filters by current organization.
    """
    def for_organization(self, organization):
        """Filter queryset for a specific organization."""
        return self.filter(organization=organization)

    def for_current_organization(self):
        """Filter queryset for the current organization from middleware."""
        organization = get_current_organization()
        if organization:
            return self.filter(organization=organization)
        return self.none()


class TenantManager(models.Manager):
    """
    Custom Manager that automatically filters queries by current organization.
    """
    def get_queryset(self):
        """Override to automatically filter by current organization."""
        queryset = TenantQuerySet(self.model, using=self._db)
        organization = get_current_organization()
        if organization:
            return queryset.filter(organization=organization)
        return queryset

    def for_organization(self, organization):
        """Get queryset for a specific organization."""
        return self.get_queryset().for_organization(organization)

    def all_organizations(self):
        """Get queryset for all organizations (bypass tenant filtering)."""
        return TenantQuerySet(self.model, using=self._db)
