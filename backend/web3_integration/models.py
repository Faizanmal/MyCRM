"""Web3 and Blockchain Integration - Models"""
import uuid

from django.contrib.auth.models import User
from django.db import models


class DataWallet(models.Model):
    """Customer data wallet for decentralized ownership"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='data_wallet')

    # Blockchain identifiers
    wallet_address = models.CharField(max_length=255, unique=True)
    public_key = models.TextField()
    blockchain_network = models.CharField(max_length=50, default='ethereum',
        choices=[('ethereum', 'Ethereum'), ('polygon', 'Polygon'), ('solana', 'Solana')])

    # Data permissions
    data_schema = models.JSONField(default=dict, help_text="Schema of user-controlled data")
    active_permissions = models.JSONField(default=list, help_text="Active access permissions granted")

    # Status
    is_verified = models.BooleanField(default=False)
    last_sync = models.DateTimeField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"DataWallet {self.wallet_address}"

    class Meta:
        verbose_name = 'Data Wallet'
        verbose_name_plural = 'Data Wallets'


class DataAccessGrant(models.Model):
    """Temporary data access grants via smart contracts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(DataWallet, on_delete=models.CASCADE, related_name='access_grants')

    # Grant details
    requester = models.CharField(max_length=255, help_text="Organization requesting access")
    data_categories = models.JSONField(default=list, help_text="Categories of data granted")
    purpose = models.TextField()

    # Smart contract
    contract_address = models.CharField(max_length=255)
    transaction_hash = models.CharField(max_length=255)

    # Duration
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(blank=True)

    is_active = models.BooleanField(default=True)
    access_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-granted_at']


class NFTLoyaltyReward(models.Model):
    """NFT-backed loyalty rewards"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_rewards')

    # NFT details
    token_id = models.CharField(max_length=255, unique=True)
    contract_address = models.CharField(max_length=255)
    metadata_uri = models.URLField()

    # Reward details
    reward_type = models.CharField(max_length=100)
    reward_name = models.CharField(max_length=255)
    description = models.TextField()
    points_value = models.IntegerField(default=0)

    # Milestone achieved
    milestone = models.CharField(max_length=255)
    milestone_date = models.DateTimeField()

    # Redemption
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(blank=True)
    redemption_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True)

    # Blockchain
    minted_at = models.DateTimeField()
    transaction_hash = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'NFT Loyalty Reward'


class SmartContract(models.Model):
    """Smart contracts for automated agreements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=100, choices=[
        ('data_access', 'Data Access Agreement'),
        ('service_level', 'Service Level Agreement'),
        ('payment', 'Payment Contract'),
        ('loyalty', 'Loyalty Program'),
    ])

    # Parties
    party_a = models.CharField(max_length=255, help_text="Wallet address of party A")
    party_b = models.CharField(max_length=255, help_text="Wallet address of party B")

    # Contract details
    terms = models.JSONField(default=dict)
    conditions = models.JSONField(default=list, help_text="Execution conditions")

    # Blockchain
    contract_address = models.CharField(max_length=255)
    deployment_tx = models.CharField(max_length=255)
    blockchain_network = models.CharField(max_length=50, default='ethereum')

    # Status
    status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'), ('active', 'Active'), ('executed', 'Executed'), ('cancelled', 'Cancelled')
    ])

    deployed_at = models.DateTimeField()
    executed_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-deployed_at']


class BlockchainTransaction(models.Model):
    """Record of blockchain transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='blockchain_transactions')

    transaction_hash = models.CharField(max_length=255, unique=True)
    blockchain_network = models.CharField(max_length=50)
    block_number = models.BigIntegerField(blank=True)

    transaction_type = models.CharField(max_length=100)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)

    value = models.CharField(max_length=100, blank=True)
    gas_used = models.BigIntegerField(blank=True)
    gas_price = models.BigIntegerField(blank=True)

    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'), ('confirmed', 'Confirmed'), ('failed', 'Failed')
    ])

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['transaction_hash'])]
