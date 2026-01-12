from rest_framework import serializers
from .models import DataWallet, DataAccessGrant, NFTLoyaltyReward, SmartContract, BlockchainTransaction


class DataWalletSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = DataWallet
        fields = ['id', 'user', 'user_email', 'wallet_address', 'public_key', 'blockchain_network',
                  'data_schema', 'active_permissions', 'is_verified', 'last_sync', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataAccessGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAccessGrant
        fields = '__all__'
        read_only_fields = ['id', 'granted_at']


class NFTLoyaltyRewardSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = NFTLoyaltyReward
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class SmartContractSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SmartContract
        fields = '__all__'
        read_only_fields = ['id']


class BlockchainTransactionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'confirmed_at']
