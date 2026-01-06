"""
White Label and Billing URL Configuration
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'partners', views.WhiteLabelPartnerViewSet, basename='partner')
router.register(r'plans', views.SubscriptionPlanViewSet, basename='plan')
router.register(r'organizations', views.OrganizationViewSet, basename='organization')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'payouts', views.PartnerPayoutViewSet, basename='payout')
router.register(r'checkout', views.CheckoutViewSet, basename='checkout')
router.register(r'branding', views.BrandingViewSet, basename='branding')

urlpatterns = [
    path('', include(router.urls)),
]
