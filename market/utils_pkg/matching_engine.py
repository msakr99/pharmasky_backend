# market/utils_pkg/matching_engine.py
import re
from fuzzywuzzy import fuzz
from django.db.models import Q
from market.models import Product, ProductMatchCache
from django.utils import timezone
from datetime import timedelta

class AdvancedProductMatcher:
    def __init__(self, threshold=75, cache_days=30):
        self.threshold = threshold
        self.cache_days = cache_days
        
    def normalize_text(self, text):
        """تطبيع النص لإزالة الاختلافات غير المهمة"""
        if not text:
            return ""
        
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.lower()
        
        return text
    
    def arabic_similarity(self, text1, text2):
        """حساب التشابه للنصوص العربية"""
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0
        sequence_similarity = fuzz.ratio(text1, text2) / 100
        
        return (jaccard_similarity * 0.6) + (sequence_similarity * 0.4)
    
    def multi_field_similarity(self, search_name, product):
        """حساب التشابه عبر حقول متعددة"""
        scores = []
        
        # مقارنة الاسم العربي
        arabic_score = self.arabic_similarity(search_name, product.name)
        scores.append(('arabic_name', arabic_score))
        
        # مقارنة الاسم الإنجليزي
        english_score = fuzz.ratio(search_name.lower(), product.e_name.lower()) / 100
        scores.append(('english_name', english_score))
        
        # أفضل درجة
        best_score = max([score for _, score in scores])
        
        return best_score, scores
    
    def get_cached_match(self, search_name):
        """الحصول على مطابقة من الـ cache"""
        cache_time = timezone.now() - timedelta(days=self.cache_days)
        
        try:
            cache_entry = ProductMatchCache.objects.filter(
                search_name=search_name,
                created_at__gte=cache_time
            ).order_by('-confidence_score').first()
            
            if cache_entry and cache_entry.confidence_score >= self.threshold/100:
                return cache_entry.product, cache_entry.confidence_score * 100
        except Exception:
            pass
        
        return None, 0
    
    def cache_match(self, search_name, product, confidence_score):
        """تخزين المطابقة في الـ cache"""
        try:
            ProductMatchCache.objects.update_or_create(
                search_name=search_name,
                product=product,
                defaults={'confidence_score': confidence_score/100}
            )
        except Exception:
            pass
    
    def find_best_match(self, search_name, products_queryset=None):
        """إيجاد أفضل مطابقة للمنتج"""
        
        # التحقق من الـ cache أولاً
        cached_product, cached_score = self.get_cached_match(search_name)
        if cached_product:
            return cached_product, cached_score
        
        if products_queryset is None:
            products_queryset = Product.objects.all()
        
        best_match = None
        best_score = 0
        
        for product in products_queryset:
            score, scores_detail = self.multi_field_similarity(search_name, product)
            
            if score > best_score:
                best_score = score
                best_match = product
        
        # تخزين في الـ cache إذا كانت النتيجة جيدة
        if best_match and best_score >= self.threshold/100:
            self.cache_match(search_name, best_match, best_score)
        
        return best_match, best_score * 100
