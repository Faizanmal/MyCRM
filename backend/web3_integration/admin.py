from django.contrib import admin

from .models import (
    BlockchainTransaction,
    DataAccessGrant,
    DataWallet,
    NFTLoyaltyReward,
    SmartContract,
)

admin.site.register(DataWallet)
admin.site.register(DataAccessGrant)
admin.site.register(NFTLoyaltyReward)
admin.site.register(SmartContract)
admin.site.register(BlockchainTransaction)
