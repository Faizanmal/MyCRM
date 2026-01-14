from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
                    BlockchainTransactionViewSet,
                    DataAccessGrantViewSet,
                    DataWalletViewSet,
                    NFTLoyaltyRewardViewSet,
                    SmartContractViewSet,
)

router = DefaultRouter()
router.register(r'wallets', DataWalletViewSet, basename='data-wallet')
router.register(r'access-grants', DataAccessGrantViewSet, basename='access-grant')
router.register(r'nft-rewards', NFTLoyaltyRewardViewSet, basename='nft-reward')
router.register(r'smart-contracts', SmartContractViewSet, basename='smart-contract')
router.register(r'transactions', BlockchainTransactionViewSet, basename='blockchain-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
