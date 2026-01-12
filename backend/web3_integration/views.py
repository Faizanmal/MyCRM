from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import DataWallet, DataAccessGrant, NFTLoyaltyReward, SmartContract, BlockchainTransaction
from .serializers import (DataWalletSerializer, DataAccessGrantSerializer, NFTLoyaltyRewardSerializer,
                          SmartContractSerializer, BlockchainTransactionSerializer)
import secrets


class DataWalletViewSet(viewsets.ModelViewSet):
    serializer_class = DataWalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataWallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_wallet(self, request):
        """Create a new data wallet for the user"""
        if DataWallet.objects.filter(user=request.user).exists():
            return Response({'error': 'Wallet already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate wallet creation
        wallet = DataWallet.objects.create(
            user=request.user,
            wallet_address=f"0x{secrets.token_hex(20)}",
            public_key=secrets.token_hex(64),
            blockchain_network='ethereum',
            is_verified=True
        )
        return Response(DataWalletSerializer(wallet).data, status=status.HTTP_201_CREATED)


class DataAccessGrantViewSet(viewsets.ModelViewSet):
    serializer_class = DataAccessGrantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        wallet = DataWallet.objects.filter(user=self.request.user).first()
        if wallet:
            return DataAccessGrant.objects.filter(wallet=wallet)
        return DataAccessGrant.objects.none()
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a data access grant"""
        grant = self.get_object()
        grant.is_active = False
        grant.revoked_at = timezone.now()
        grant.save()
        return Response({'status': 'revoked'})


class NFTLoyaltyRewardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NFTLoyaltyRewardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NFTLoyaltyReward.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        """Redeem an NFT loyalty reward"""
        reward = self.get_object()
        if reward.is_redeemed:
            return Response({'error': 'Already redeemed'}, status=status.HTTP_400_BAD_REQUEST)
        
        reward.is_redeemed = True
        reward.redeemed_at = timezone.now()
        reward.redemption_value = reward.points_value * 10
        reward.save()
        return Response(NFTLoyaltyRewardSerializer(reward).data)


class SmartContractViewSet(viewsets.ModelViewSet):
    serializer_class = SmartContractSerializer
    permission_classes = [IsAuthenticated]
    queryset = SmartContract.objects.all()


class BlockchainTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BlockchainTransaction.objects.filter(user=self.request.user)
