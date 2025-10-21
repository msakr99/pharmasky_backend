"""
API Views for AI Agent Service
These endpoints are designed for programmatic access by the FastAPI agent
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from market.models import Product, StoreProductCode
from market.ai_serializers import (
    DrugSearchResponseSerializer,
    DrugStockCheckSerializer,
    DrugStockResponseSerializer,
    CreateOrderRequestSerializer,
    CreateOrderResponseSerializer
)
from accounts.models import Pharmacy, Store


class DrugSearchAPIView(APIView):
    """
    Search drugs by name, compound, or company
    
    GET /market/ai/drugs/search/?q=<query>&limit=10
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response({
                'results': [],
                'count': 0,
                'query': query
            }, status=status.HTTP_200_OK)
        
        # Search in name, e_name, effective_material, company, category
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(e_name__icontains=query) |
            Q(effective_material__icontains=query) |
            Q(company__name__icontains=query) |
            Q(company__e_name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('company', 'category')[:limit]
        
        results = []
        for product in products:
            # Check if in stock (has codes)
            stock_count = StoreProductCode.objects.filter(
                product=product
            ).count()
            
            results.append({
                'id': product.id,
                'name': product.name,
                'e_name': product.e_name,
                'company': product.company.name,
                'category': product.category.name,
                'public_price': float(product.public_price),
                'effective_material': product.effective_material,
                'shape': product.shape,
                'in_stock': stock_count > 0,
                'available_quantity': stock_count
            })
        
        return Response({
            'results': results,
            'count': len(results),
            'query': query
        }, status=status.HTTP_200_OK)


class DrugStockCheckAPIView(APIView):
    """
    Check stock availability for a product
    
    POST /market/ai/drugs/stock/
    Body: {"product_id": 123, "store_id": 1 (optional)}
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = DrugStockCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid request',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        store_id = serializer.validated_data.get('store_id')
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check stock
        stock_query = StoreProductCode.objects.filter(product=product)
        
        if store_id:
            stock_query = stock_query.filter(store_id=store_id)
        
        total_quantity = stock_query.count()
        
        # Get breakdown by store
        stores_data = []
        if not store_id:
            stores_stock = stock_query.values('store__id', 'store__name').annotate(
                quantity=Count('id')
            )
            for item in stores_stock:
                stores_data.append({
                    'store_id': item['store__id'],
                    'store_name': item['store__name'],
                    'quantity': item['quantity']
                })
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'available': total_quantity > 0,
            'quantity': total_quantity,
            'stores': stores_data
        }, status=status.HTTP_200_OK)


class DrugRecommendationAPIView(APIView):
    """
    Get alternative/related drugs
    
    GET /market/ai/drugs/<id>/recommendations/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get alternatives and instances
        alternatives = product.alternatives.all().select_related('company', 'category')
        instances = product.instances.all().select_related('company', 'category')
        
        results = []
        for alt in alternatives:
            results.append({
                'id': alt.id,
                'name': alt.name,
                'e_name': alt.e_name,
                'company': alt.company.name,
                'public_price': float(alt.public_price),
                'type': 'alternative'
            })
        
        for inst in instances:
            results.append({
                'id': inst.id,
                'name': inst.name,
                'e_name': inst.e_name,
                'company': inst.company.name,
                'public_price': float(inst.public_price),
                'type': 'instance'
            })
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'recommendations': results,
            'count': len(results)
        }, status=status.HTTP_200_OK)


class CreateOrderAPIView(APIView):
    """
    Create an order from AI agent
    
    POST /market/ai/orders/create/
    Body: {
        "pharmacy_id": 123,
        "items": [
            {"product_id": 1, "quantity": 10},
            {"product_id": 2, "quantity": 5}
        ],
        "notes": "Order from AI agent"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CreateOrderRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'بيانات غير صحيحة',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pharmacy_id = serializer.validated_data['pharmacy_id']
        items = serializer.validated_data['items']
        notes = serializer.validated_data.get('notes', '')
        
        # Verify pharmacy exists
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return Response({
                'success': False,
                'message': 'الصيدلية غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify all products exist
        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(id__in=product_ids)
        
        if products.count() != len(product_ids):
            return Response({
                'success': False,
                'message': 'بعض المنتجات غير موجودة'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Actually create the order in the system
        # This depends on your existing order model structure
        # For now, we'll return a success response with simulated order ID
        
        order_details = {
            'pharmacy': pharmacy.name,
            'items_count': len(items),
            'total_items': sum(item['quantity'] for item in items),
            'notes': notes
        }
        
        return Response({
            'success': True,
            'order_id': 99999,  # Simulated - replace with actual order creation
            'message': f'تم إنشاء الطلب بنجاح للصيدلية {pharmacy.name}',
            'details': order_details
        }, status=status.HTTP_201_CREATED)


class PharmacyInfoAPIView(APIView):
    """
    Get pharmacy information
    
    GET /market/ai/pharmacies/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pharmacy_id):
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return Response({
                'error': 'الصيدلية غير موجودة'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': pharmacy.id,
            'name': pharmacy.name,
            'phone': pharmacy.phone if hasattr(pharmacy, 'phone') else None,
            'address': pharmacy.address if hasattr(pharmacy, 'address') else None,
            # Add more fields as needed based on your Pharmacy model
        }, status=status.HTTP_200_OK)

