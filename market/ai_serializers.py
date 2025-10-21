"""
Serializers specifically for AI Agent Service integration
These provide comprehensive data for RAG and MCP operations
"""
from rest_framework import serializers
from market.models import Product, ProductCode, StoreProductCode, Company, Category
from accounts.models import Pharmacy


class DrugDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive drug/product details for RAG ingestion
    """
    company = serializers.CharField(source='company.name')
    company_english = serializers.CharField(source='company.e_name')
    category = serializers.CharField(source='category.name')
    category_english = serializers.CharField(source='category.e_name')
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'e_name',
            'company',
            'company_english',
            'category',
            'category_english',
            'public_price',
            'effective_material',
            'letter',
            'shape',
            'needed',
            'is_illegal',
            'fridge',
        ]


class DrugSearchResponseSerializer(serializers.Serializer):
    """Response for drug search queries"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    e_name = serializers.CharField()
    company = serializers.CharField()
    category = serializers.CharField()
    public_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    effective_material = serializers.CharField()
    shape = serializers.CharField()
    in_stock = serializers.BooleanField(default=True)
    available_quantity = serializers.IntegerField(default=0, required=False)


class DrugStockCheckSerializer(serializers.Serializer):
    """Request for stock checking"""
    product_id = serializers.IntegerField()
    store_id = serializers.IntegerField(required=False)


class DrugStockResponseSerializer(serializers.Serializer):
    """Response for stock check"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    available = serializers.BooleanField()
    quantity = serializers.IntegerField()
    stores = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )


class CreateOrderRequestSerializer(serializers.Serializer):
    """Request to create an order via AI agent"""
    pharmacy_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, value):
        """Validate items structure"""
        for item in value:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'product_id' and 'quantity'"
                )
            if item['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be positive")
        return value


class CreateOrderResponseSerializer(serializers.Serializer):
    """Response for order creation"""
    success = serializers.BooleanField()
    order_id = serializers.IntegerField(required=False)
    message = serializers.CharField()
    details = serializers.DictField(required=False)

