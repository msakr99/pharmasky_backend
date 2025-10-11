from decimal import Decimal
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, GenericAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.apps import apps
from django.contrib.auth import get_user_model
from accounts.permissions import *
from core.views.mixins import PDFFileMixin
from core.views.renderers import PDFRenderer
from django.utils.translation import activate
from finance.choices import NEGATIVE_AFFECTING_TRANSACTIONS, POSTIVE_AFFECTING_TRANSACTIONS, SafeTransactionTypeChoice
from finance.filters import AccountTransactionFilter, PurchasePaymentFilter, SalePaymentFilter
from finance.models import Account, AccountTransaction, PurchasePayment, SafeTransaction, SalePayment, Expense
from finance.serializers import (
    AccountTransactionReadSerializer,
    AccountUpdateSerializer,
    PurchasePaymentCreateSerializer,
    PurchasePaymentReadSerializer,
    PurchasePaymentUpdateSerializer,
    SafeSerializer,
    SafeTransactionSerializer,
    SalePaymentCreateSerializer,
    SalePaymentReadSerializer,
    SalePaymentUpdateSerializer,
    ExpenseSerializer,
    CollectionScheduleSerializer,
    AccountsPayableSerializer,
    AccountStatementPDFSerializer,
)
from finance.utils import delete_payment
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime

get_model = apps.get_model


class AccountUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = AccountUpdateSerializer
    queryset = AccountTransaction.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Account.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class AccountTransactionListAPIView(ListAPIView):
    permission_classes = [StaffRoleAuthentication]
    serializer_class = AccountTransactionReadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AccountTransactionFilter
    ordering = ("-at",)

    def get_queryset(self):
        user = self.request.user

        queryset = AccountTransaction.objects.select_related('account').all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(account__user=user) | models.Q(account__user__profile__sales=user))
            case Role.DATA_ENTRY:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__data_entry=user)
                )
            case Role.DELIVERY:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__delivery=user)
                )
            case Role.MANAGER:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__manager=user)
                )
            case Role.AREA_MANAGER:
                queryset = queryset.filter(
                    models.Q(account__user=user) | models.Q(account__user__profile__area_manager=user)
                )

        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list to add running balance calculation
        """
        from finance.choices import NEGATIVE_AFFECTING_TRANSACTIONS, POSTIVE_AFFECTING_TRANSACTIONS
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get account from query params to calculate running balance
        account_id = request.query_params.get('account', None)
        user_id = request.query_params.get('user', None)
        
        # Order by date (oldest first) to calculate running balance
        transactions = queryset.order_by('at', 'id')
        
        # Calculate running balance if filtering by specific account/user
        if account_id or user_id:
            # Get the account
            account = None
            if account_id:
                try:
                    account = Account.objects.get(pk=account_id)
                except Account.DoesNotExist:
                    pass
            elif user_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user_obj = User.objects.get(pk=user_id)
                    account = getattr(user_obj, 'account', None)
                except:
                    pass
            
            if account:
                # Get all transactions for this account ordered by date
                all_transactions = AccountTransaction.objects.filter(
                    account=account
                ).order_by('at', 'id')
                
                # Calculate running balance for each transaction
                running_balance = Decimal('0.00')
                transaction_balances = {}
                
                for txn in all_transactions:
                    # Determine if this transaction increases or decreases balance
                    if txn.type in NEGATIVE_AFFECTING_TRANSACTIONS:
                        running_balance -= txn.amount
                    elif txn.type in POSTIVE_AFFECTING_TRANSACTIONS:
                        running_balance += txn.amount
                    
                    transaction_balances[txn.id] = running_balance
                
                # Add balance_after to each transaction in queryset
                transactions_list = list(transactions)
                for txn in transactions_list:
                    txn.balance_after = transaction_balances.get(txn.id, Decimal('0.00'))
                
                # Reverse to show newest first
                transactions_list.reverse()
                
                # Paginate if needed
                page = self.paginate_queryset(transactions_list)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                
                serializer = self.get_serializer(transactions_list, many=True)
                return Response(serializer.data)
        
        # If no specific account, return without running balance
        # Order by newest first for display
        transactions = queryset.order_by('-at', '-id')
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class PurchasePaymentListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PurchasePaymentReadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = PurchasePaymentFilter
    search_fields = ["user__name", "user__e_name", "user__username", "remarks"]
    ordering = ("-at",)

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case r:
                queryset = queryset.filter(models.Q(user=user))

        return queryset


class PurchasePaymentCreateView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = PurchasePaymentCreateSerializer
    queryset = PurchasePayment.objects.all()


class PurchasePaymentUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = PurchasePaymentUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class PurchasePaymentDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = PurchasePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        delete_payment(instance)


class SalePaymentListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalePaymentReadSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = SalePaymentFilter
    search_fields = ["user__name", "user__e_name", "user__username", "remarks"]
    ordering = ("-at",)

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case r:
                queryset = queryset.filter(models.Q(user=user))

        return queryset


class SalePaymentCreateView(CreateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = SalePaymentCreateSerializer
    queryset = SalePayment.objects.all()


class SalePaymentUpdateAPIView(UpdateAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]
    serializer_class = SalePaymentUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset


class SalePaymentDestroyAPIView(DestroyAPIView):
    permission_classes = [SalesRoleAuthentication, ManagerRoleAuthentication, AreaManagerRoleAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = SalePayment.objects.select_related("user", "user__account").all()

        if user.is_superuser:
            return queryset

        user_role = user.role

        match user_role:
            case Role.SALES:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales=user))
            case Role.MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__manager=user))
            case Role.AREA_MANAGER:
                queryset = queryset.filter(models.Q(user=user) | models.Q(user__profile__sales__area_manager=user))
            case _r:
                queryset = queryset.none()

        return queryset

    def perform_destroy(self, instance):
        delete_payment(instance)


class SafeTransactionListAPIView(ListAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeTransactionSerializer

    def get_queryset(self):
        queryset = SafeTransaction.objects.all()
        return queryset


class SafeTransactionCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeTransactionSerializer
    queryset = SafeTransaction.objects.all()


class SafeRetrieveAPIView(GenericAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = SafeSerializer

    def get_queryset(self):
        sale_payment_total_amount = SalePayment.objects.aggregate(total_amount=models.Sum("amount"))[
            "total_amount"
        ] or Decimal("0.00")

        purchase_payment_total_amount = PurchasePayment.objects.aggregate(total_amount=models.Sum("amount"))[
            "total_amount"
        ] or Decimal("0.00")

        safe_total_amount = (
            (
                SafeTransaction.objects.annotate(
                    signed_amount=models.Case(
                        models.When(type=SafeTransactionTypeChoice.WITHDRAWAL, then=models.F("amount") * -1),
                        default=models.F("amount"),
                    )
                ).aggregate(total_amount=models.Sum("signed_amount"))["total_amount"]
                or Decimal("0.00")
            )
            + sale_payment_total_amount
            - purchase_payment_total_amount
        )

        debt_total_amount = Account.objects.filter(balance__gte=0).aggregate(total_amount=models.Sum("balance"))[
            "total_amount"
        ] or Decimal("0.00")

        credit_total_amount = Account.objects.filter(balance__lt=0).aggregate(total_amount=models.Sum("balance") * -1)[
            "total_amount"
        ] or Decimal("0.00")

        inventory_total_amount = get_model("inventory", "InventoryItem").objects.aggregate(
            total_amount=models.Sum("purchase_sub_total")
        )["total_amount"] or Decimal("0.00")
        
        # حساب إجمالي المصاريف (تخصم من رأس المال)
        expenses_total_amount = Expense.objects.aggregate(
            total_amount=models.Sum("amount")
        )["total_amount"] or Decimal("0.00")

        return {
            "safe_total_amount": safe_total_amount,
            "debt_total_amount": debt_total_amount,
            "credit_total_amount": credit_total_amount,
            "inventory_total_amount": inventory_total_amount,
            "expenses_total_amount": expenses_total_amount,
            "total_amount": safe_total_amount + credit_total_amount + inventory_total_amount - debt_total_amount - expenses_total_amount,
        }

    def get(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class ExpenseListAPIView(ListAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ExpenseSerializer
    ordering_fields = ["expense_date", "amount", "category", "type"]
    search_fields = ["description", "recipient"]
    
    def get_queryset(self):
        queryset = Expense.objects.all()
        
        # فلترة حسب النوع
        expense_type = self.request.query_params.get('type', None)
        if expense_type:
            queryset = queryset.filter(type=expense_type)
        
        # فلترة حسب الفئة
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # فلترة حسب الشهر
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        if month and year:
            queryset = queryset.filter(
                expense_date__month=month,
                expense_date__year=year
            )
        
        return queryset


class ExpenseCreateAPIView(CreateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()


class ExpenseUpdateAPIView(UpdateAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()


class ExpenseDestroyAPIView(DestroyAPIView):
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()


class CollectionScheduleAPIView(GenericAPIView):
    """
    قائمة مواعيد التحصيلات المتوقعة
    Collection Schedule - Expected payment dates based on payment periods
    
    Query Parameters:
    - search: البحث باسم العميل أو رقم الهاتف
    - date_from: تاريخ البداية (YYYY-MM-DD)
    - date_to: تاريخ النهاية (YYYY-MM-DD)
    - overdue_only: فقط المتأخرين (true/false)
    
    Returns list of pharmacies with:
    - Customer name (اسم العميل)
    - Expected collection date (تاريخ التحصيل المتوقع)
    - Outstanding amount (المبلغ المستحق)
    - Total balance (إجمالي الرصيد)
    """
    permission_classes = [StaffRoleAuthentication]
    serializer_class = CollectionScheduleSerializer
    
    def get(self, request, *args, **kwargs):
        User = get_user_model()
        current_date = timezone.now()
        
        # Get query parameters
        search_term = request.query_params.get('search', '').strip()
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        overdue_only = request.query_params.get('overdue_only', '').lower() == 'true'
        
        # Get all pharmacies with payment periods and negative balance (مديونين)
        pharmacies = (
            User.objects
            .filter(role=Role.PHARMACY)
            .select_related('profile', 'profile__payment_period', 'account')
            .exclude(account__balance__gte=0)  # Only those with debt (balance < 0)
        )
        
        # Apply search filter
        if search_term:
            pharmacies = pharmacies.filter(
                models.Q(name__icontains=search_term) |
                models.Q(e_name__icontains=search_term) |
                models.Q(username__icontains=search_term)
            )
        
        # Filter based on user role
        user = request.user
        if not user.is_superuser:
            match user.role:
                case Role.SALES:
                    pharmacies = pharmacies.filter(profile__sales=user)
                case Role.MANAGER:
                    pharmacies = pharmacies.filter(profile__manager=user)
                case Role.AREA_MANAGER:
                    pharmacies = pharmacies.filter(profile__area_manager=user)
                case _:
                    pharmacies = pharmacies.none()
        
        # Build collection schedule data
        schedule_data = []
        total_outstanding = Decimal('0.00')
        
        for pharmacy in pharmacies:
            # Skip if no profile or account
            if not hasattr(pharmacy, 'profile') or not hasattr(pharmacy, 'account'):
                continue
            
            profile = pharmacy.profile
            account = pharmacy.account
            outstanding_balance = abs(account.balance)  # Convert negative to positive
            
            # Skip if no outstanding balance
            if outstanding_balance <= 0:
                continue
            
            # Calculate expected collection date
            expected_date = None
            days_until = None
            is_overdue = False
            payment_period_name = None
            period_days = None
            
            if profile.payment_period and profile.latest_invoice_date:
                payment_period_name = profile.payment_period.name
                period_days = profile.payment_period.period_in_days
                expected_date = profile.latest_invoice_date + timedelta(days=period_days)
                days_until = (expected_date - current_date).days
                is_overdue = days_until < 0
            
            # Calculate penalty and cashback
            penalty_percentage = profile.late_payment_penalty_percentage or Decimal('0.20')
            cashback_percentage = profile.early_payment_cashback_percentage or Decimal('0.10')
            penalty_amount = Decimal('0.00')
            cashback_amount = Decimal('0.00')
            total_with_penalty = outstanding_balance
            total_with_cashback = outstanding_balance
            
            if days_until is not None:
                if days_until < 0:
                    # Late payment - calculate penalty
                    late_days = abs(days_until)
                    penalty_amount = (outstanding_balance * penalty_percentage * late_days) / 100
                    total_with_penalty = outstanding_balance + penalty_amount
                elif days_until > 0:
                    # Early payment - calculate cashback
                    early_days = days_until
                    cashback_amount = (outstanding_balance * cashback_percentage * early_days) / 100
                    total_with_cashback = outstanding_balance - cashback_amount
            
            # Create schedule entry
            entry = {
                'user_id': pharmacy.id,
                'customer_name': pharmacy.name,
                'username': str(pharmacy.username),
                'payment_period_name': payment_period_name or 'غير محدد',
                'period_in_days': period_days or 0,
                'latest_invoice_date': profile.latest_invoice_date,
                'expected_collection_date': expected_date,
                'days_until_collection': days_until or 0,
                'outstanding_balance': outstanding_balance,
                'is_overdue': is_overdue,
                # Penalty
                'penalty_percentage': penalty_percentage,
                'penalty_amount': penalty_amount,
                'total_with_penalty': total_with_penalty,
                # Cashback
                'cashback_percentage': cashback_percentage,
                'cashback_amount': cashback_amount,
                'total_with_cashback': total_with_cashback,
            }
            
            # Apply overdue filter
            if overdue_only and not is_overdue:
                continue
            
            # Apply date range filter
            if expected_date:
                if date_from:
                    try:
                        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                        if expected_date < date_from_obj:
                            continue
                    except ValueError:
                        pass  # Invalid date format, skip filter
                
                if date_to:
                    try:
                        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                        if expected_date > date_to_obj:
                            continue
                    except ValueError:
                        pass  # Invalid date format, skip filter
            
            schedule_data.append(entry)
            total_outstanding += outstanding_balance
        
        # Sort by expected collection date (overdue first, then by date)
        schedule_data.sort(
            key=lambda x: (
                not x['is_overdue'],  # Overdue first (False comes before True)
                x['expected_collection_date'] if x['expected_collection_date'] else current_date
            )
        )
        
        # Serialize data
        serializer = self.get_serializer(schedule_data, many=True)
        
        return Response({
            'count': len(schedule_data),
            'total_outstanding_amount': total_outstanding,
            'results': serializer.data
        })


class AccountsPayableAPIView(GenericAPIView):
    """
    قائمة الحسابات الدائنة - الفلوس اللي علينا
    Accounts Payable - Money we owe to suppliers/stores
    
    Query Parameters:
    - search: البحث باسم المورد أو رقم الهاتف
    - role: فلتر حسب نوع المستخدم (STORE, SALES, etc.)
    - min_amount: الحد الأدنى للمبلغ
    
    Returns list of suppliers/stores with positive balance (we owe them)
    """
    permission_classes = [ManagerRoleAuthentication]
    serializer_class = AccountsPayableSerializer
    
    def get(self, request, *args, **kwargs):
        User = get_user_model()
        current_date = timezone.now()
        
        # Get query parameters
        search_term = request.query_params.get('search', '').strip()
        role_filter = request.query_params.get('role', '').strip().upper()
        min_amount = request.query_params.get('min_amount', None)
        
        # Get all users with positive balance (we owe them money)
        # positive balance = الشركة مديونة لهم
        accounts = (
            Account.objects
            .filter(balance__gt=0)
            .select_related('user')
        )
        
        # Apply search filter on user
        if search_term:
            accounts = accounts.filter(
                models.Q(user__name__icontains=search_term) |
                models.Q(user__e_name__icontains=search_term) |
                models.Q(user__username__icontains=search_term)
            )
        
        # Apply role filter
        if role_filter:
            accounts = accounts.filter(user__role=role_filter)
        
        # Apply minimum amount filter
        if min_amount:
            try:
                min_amount_decimal = Decimal(min_amount)
                accounts = accounts.filter(balance__gte=min_amount_decimal)
            except (ValueError, TypeError):
                pass  # Invalid number, skip filter
        
        # Build accounts payable data
        payable_data = []
        total_payable = Decimal('0.00')
        
        for account in accounts:
            try:
                user = account.user
                amount_owed = account.balance
                
                # Get last payment date
                last_payment = PurchasePayment.objects.filter(
                    user=user
                ).order_by('-at').first()
                
                last_payment_date = last_payment.at if last_payment else None
                days_since_last_payment = 0
                
                if last_payment_date:
                    try:
                        # Calculate days difference
                        time_diff = current_date - last_payment_date
                        days_since_last_payment = time_diff.days
                    except Exception:
                        days_since_last_payment = 0
                
                # Get last purchase date (from invoices)
                last_purchase_date = None
                try:
                    PurchaseInvoice = get_model('invoices', 'PurchaseInvoice')
                    last_purchase_invoice = PurchaseInvoice.objects.filter(
                        store=user
                    ).order_by('-created_at').first()
                    
                    if last_purchase_invoice:
                        last_purchase_date = last_purchase_invoice.created_at
                except Exception:
                    # If model doesn't exist or error, just skip
                    pass
                
                # Get role label
                try:
                    role_label = user.get_role_display()
                except Exception:
                    role_label = user.role
                
                entry = {
                    'user_id': user.id,
                    'supplier_name': user.name,
                    'username': str(user.username),
                    'role': user.role,
                    'role_label': role_label,
                    'amount_owed': amount_owed,
                    'last_payment_date': last_payment_date,
                    'last_purchase_date': last_purchase_date,
                    'days_since_last_payment': days_since_last_payment,
                }
                
                payable_data.append(entry)
                total_payable += amount_owed
            except Exception as e:
                # Skip this account if there's an error
                continue
        
        # Sort by amount owed (descending)
        payable_data.sort(key=lambda x: x['amount_owed'], reverse=True)
        
        # Serialize data
        serializer = self.get_serializer(payable_data, many=True)
        
        return Response({
            'count': len(payable_data),
            'total_payable_amount': total_payable,
            'results': serializer.data
        })


class AccountStatementPDFAPIView(PDFFileMixin, GenericAPIView):
    """
    طباعة كشف الحساب PDF
    Account Statement PDF Export
    
    Query Parameters:
    - user: معرف المستخدم (مطلوب)
    - type: نوع المعاملة (اختياري)
    """
    permission_classes = [StaffRoleAuthentication]
    renderer_classes = [PDFRenderer]
    serializer_class = AccountStatementPDFSerializer
    template_name = "finance/pdf/account_statement.html"
    
    def get_template_context(self):
        return {
            "timestamp": timezone.now().strftime("%d-%m-%Y %H:%M"),
            "customer_name": self.customer_name,
            "username": self.username,
            "current_balance": self.current_balance,
        }
    
    def get_filename(self, request=None, *args, **kwargs):
        NOW = timezone.now().strftime("%d-%m-%Y")
        return f"Account Statement - {self.customer_name} - {NOW}.pdf"
    
    def get(self, request, *args, **kwargs):
        from finance.choices import NEGATIVE_AFFECTING_TRANSACTIONS, POSTIVE_AFFECTING_TRANSACTIONS
        
        activate("ar")
        
        # Get user_id from query params
        user_id = request.query_params.get('user', None)
        type_filter = request.query_params.get('type', None)
        
        if not user_id:
            return Response({
                'error': 'user parameter is required'
            }, status=400)
        
        # Get the user and account
        try:
            User = get_user_model()
            user_obj = User.objects.select_related('account').get(pk=user_id)
            account = getattr(user_obj, 'account', None)
            
            # Set context variables early (before finalize_response is called)
            self.customer_name = user_obj.name
            self.username = str(user_obj.username)
            self.current_balance = account.balance if account else Decimal('0.00')
            
            if not account:
                return Response({
                    'error': 'User does not have an account'
                }, status=404)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=404)
        
        # Check permissions based on role
        request_user = request.user
        if not request_user.is_superuser:
            allowed = False
            match request_user.role:
                case Role.SALES:
                    allowed = (account.user == request_user or 
                              getattr(user_obj.profile, 'sales', None) == request_user)
                case Role.MANAGER:
                    allowed = (account.user == request_user or 
                              getattr(user_obj.profile, 'manager', None) == request_user)
                case Role.AREA_MANAGER:
                    allowed = (account.user == request_user or 
                              getattr(user_obj.profile, 'area_manager', None) == request_user)
            
            if not allowed:
                return Response({
                    'error': 'Permission denied'
                }, status=403)
        
        # Get all transactions for this account
        queryset = AccountTransaction.objects.filter(account=account)
        
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Order by date (oldest first) for running balance calculation
        transactions = queryset.order_by('at', 'id')
        
        # Calculate running balance
        running_balance = Decimal('0.00')
        statement_data = []
        
        for txn in transactions:
            # Determine if this transaction increases or decreases balance
            if txn.type in NEGATIVE_AFFECTING_TRANSACTIONS:
                running_balance -= txn.amount
            elif txn.type in POSTIVE_AFFECTING_TRANSACTIONS:
                running_balance += txn.amount
            
            statement_data.append({
                'transaction_date': txn.at.strftime("%Y-%m-%d %H:%M"),
                'type_label': txn.get_type_display(),
                'amount': txn.amount,
                'balance_after': running_balance,
                'remarks': getattr(txn.related_object, 'remarks', '') if txn.related_object else '',
            })
        
        # Reverse to show newest first in PDF
        statement_data.reverse()
        
        # Serialize
        serializer = self.get_serializer(statement_data, many=True)
        return Response(serializer.data)
