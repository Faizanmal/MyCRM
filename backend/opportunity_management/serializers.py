from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Opportunity, OpportunityActivity, OpportunityProduct, OpportunityStage, Product

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'price', 'currency',
            'category', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OpportunityProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OpportunityProduct
        fields = [
            'id', 'opportunity', 'product', 'product_name', 'quantity',
            'unit_price', 'discount_percentage', 'total_price'
        ]
        read_only_fields = ['id', 'total_price']


class OpportunityStageSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = OpportunityStage
        fields = [
            'id', 'name', 'description', 'probability', 'order',
            'is_closed', 'is_won', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class OpportunityActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = OpportunityActivity
        fields = [
            'id', 'opportunity', 'activity_type', 'subject', 'description',
            'user', 'user_name', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class OpportunitySerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    contact_name = serializers.CharField(source='contact.full_name', read_only=True)
    weighted_amount = serializers.ReadOnlyField()
    products = OpportunityProductSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'contact', 'contact_name', 'company_name',
            'stage', 'probability', 'amount', 'currency', 'weighted_amount',
            'assigned_to', 'assigned_to_name', 'owner', 'owner_name',
            'expected_close_date', 'actual_close_date', 'last_activity_date',
            'notes', 'tags', 'custom_fields', 'products',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OpportunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = [
            'name', 'description', 'contact', 'company_name', 'stage',
            'probability', 'amount', 'currency', 'assigned_to',
            'expected_close_date', 'notes', 'tags', 'custom_fields'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class OpportunityBulkUpdateSerializer(serializers.Serializer):
    opportunity_ids = serializers.ListField(child=serializers.IntegerField())
    updates = serializers.DictField()

    def validate_opportunity_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one opportunity ID is required.")
        return value
