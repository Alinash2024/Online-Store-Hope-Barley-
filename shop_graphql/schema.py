# shop_graphql/schema.py
import graphene
from graphene_django import DjangoObjectType
from django.db.models import QuerySet, Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Optional
from users.models import User
from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review


class UserType(DjangoObjectType):
    """GraphQL type for User model."""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_joined")


class ProductType(DjangoObjectType):
    """GraphQL type for Product model."""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "category",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
        )


class OrderType(DjangoObjectType):
    """GraphQL type for Order model."""

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
            "is_paid",
            "total_price",
            "status",
            "full_name",
            "phone",
            "city",
            "address",
            "payment_method",
        )


class OrderItemType(DjangoObjectType):
    """GraphQL type for OrderItem model."""

    class Meta:
        model = OrderItem
        fields = ("id", "order", "product", "quantity", "price")


class ReviewType(DjangoObjectType):
    """GraphQL type for Review model."""

    class Meta:
        model = Review
        fields = ("id", "product", "user", "rating", "comment", "created_at")


class OrderAnalyticsType(graphene.ObjectType):
    """GraphQL type for order analytics data."""

    total_revenue = graphene.Decimal()
    total_orders = graphene.Int()
    average_order_value = graphene.Decimal()


class ProductAnalyticsType(graphene.ObjectType):
    """GraphQL type for product analytics data."""

    total_products = graphene.Int()
    out_of_stock_count = graphene.Int()


class UserAnalyticsType(graphene.ObjectType):
    """GraphQL type for user analytics data."""

    total_users = graphene.Int()
    active_users_last_30_days = graphene.Int()
    repeat_customers = graphene.Int()


class Query(graphene.ObjectType):
    """Main GraphQL query class containing all available queries."""

    all_products = graphene.List(ProductType)
    product_by_id = graphene.Field(ProductType, id=graphene.Int(required=True))

    all_orders = graphene.List(OrderType)
    orders_by_user = graphene.List(
        OrderType, user_id=graphene.Int(required=True)
    )

    all_reviews = graphene.List(ReviewType)
    reviews_by_product = graphene.List(
        ReviewType, product_id=graphene.Int(required=True)
    )

    order_analytics = graphene.Field(OrderAnalyticsType)
    product_analytics = graphene.Field(ProductAnalyticsType)
    user_analytics = graphene.Field(UserAnalyticsType)
    popular_products = graphene.List(ProductType, limit=graphene.Int())
    low_stock_products = graphene.List(ProductType, threshold=graphene.Int())
    active_users = graphene.List(UserType, days=graphene.Int())
    repeat_customers = graphene.List(UserType)

    def resolve_all_products(
        self, info: graphene.ResolveInfo
    ) -> QuerySet[Product]:
        """
        Resolve all products query.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            QuerySet of all Product objects
        """
        return Product.objects.all()

    def resolve_product_by_id(
        self, info: graphene.ResolveInfo, id: int
    ) -> Optional[Product]:
        """
        Resolve product by ID query.

        Args:
            info: GraphQL resolve info containing request context
            id: Product ID to retrieve

        Returns:
            Product object or None if not found
        """
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_all_orders(
        self, info: graphene.ResolveInfo
    ) -> QuerySet[Order]:
        """
        Resolve all orders query. Only staff can see all orders.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            QuerySet of Order objects accessible to the user
        """
        if info.context.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=info.context.user)

    def resolve_orders_by_user(
        self, info: graphene.ResolveInfo, user_id: int
    ) -> QuerySet[Order]:
        """
        Resolve orders by user query.
        Only staff or the user themselves can see orders.

        Args:
            info: GraphQL resolve info containing request context
            user_id: ID of the user whose orders to retrieve

        Returns:
            QuerySet of Order objects for the specified user
        """
        if info.context.user.is_staff or info.context.user.id == user_id:
            return Order.objects.filter(user_id=user_id)
        return Order.objects.none()

    def resolve_all_reviews(
        self, info: graphene.ResolveInfo
    ) -> QuerySet[Review]:
        """
        Resolve all reviews query.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            QuerySet of all Review objects
        """
        return Review.objects.all()

    def resolve_reviews_by_product(
        self, info: graphene.ResolveInfo, product_id: int
    ) -> QuerySet[Review]:
        """
        Resolve reviews by product query.

        Args:
            info: GraphQL resolve info containing request context
            product_id: ID of the product whose reviews to retrieve

        Returns:
            QuerySet of Review objects for the specified product
        """
        return Review.objects.filter(product_id=product_id)

    def resolve_order_analytics(
        self, info: graphene.ResolveInfo
    ) -> Optional[OrderAnalyticsType]:
        """
        Resolve order analytics query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            OrderAnalyticsType object with analytics
            data or None if user is not staff
        """
        if not info.context.user.is_staff:
            return None

        total_revenue = Order.objects.filter(is_paid=True).aggregate(
            total=Sum("total_price")
        )["total"] or Decimal("0.00")

        total_orders = Order.objects.count()
        paid_orders = Order.objects.filter(is_paid=True)
        total_paid_amount = paid_orders.aggregate(total=Sum("total_price"))[
            "total"
        ] or Decimal("0.00")
        num_paid_orders = paid_orders.count()
        average_order_value = Decimal("0.00")
        if num_paid_orders > 0:
            average_order_value = total_paid_amount / num_paid_orders

        return OrderAnalyticsType(
            total_revenue=total_revenue,
            total_orders=total_orders,
            average_order_value=average_order_value,
        )

    def resolve_product_analytics(
        self, info: graphene.ResolveInfo
    ) -> Optional[ProductAnalyticsType]:
        """
        Resolve product analytics query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            ProductAnalyticsType object with analytics data
            or None if user is not staff
        """
        if not info.context.user.is_staff:
            return None

        total_products = Product.objects.count()

        out_of_stock_count = Product.objects.filter(stock=0).count()

        return ProductAnalyticsType(
            total_products=total_products,
            out_of_stock_count=out_of_stock_count,
        )

    def resolve_user_analytics(
        self, info: graphene.ResolveInfo
    ) -> Optional[UserAnalyticsType]:
        """
        Resolve user analytics query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            UserAnalyticsType object with analytics data
            or None if user is not staff
        """

        if not info.context.user.is_staff:
            return None

        total_users = User.objects.count()

        thirty_days_ago = timezone.now() - timedelta(days=30)
        active_users_last_30_days = (
            User.objects.filter(order_set__created_at__gte=thirty_days_ago)
            .distinct()
            .count()
        )

        repeat_customers = (
            User.objects.annotate(order_count=Count("order_set"))
            .filter(order_count__gt=1)
            .count()
        )

        return UserAnalyticsType(
            total_users=total_users,
            active_users_last_30_days=active_users_last_30_days,
            repeat_customers=repeat_customers,
        )

    def resolve_popular_products(
        self, info: graphene.ResolveInfo, limit: int = 10
    ) -> QuerySet[Product]:
        """
        Resolve popular products query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context
            limit: Maximum number of products to return

        Returns:
            QuerySet of popular Product objects
        """

        if not info.context.user.is_staff:
            return Product.objects.none()

        return (
            Product.objects.annotate(total_sold=Sum("orderitem_set__quantity"))
            .filter(total_sold__gt=0)
            .order_by("-total_sold")[:limit]
        )

    def resolve_low_stock_products(
        self, info: graphene.ResolveInfo, threshold: int = 5
    ) -> QuerySet[Product]:
        """
        Resolve low stock products query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context
            threshold: Stock threshold to consider as low stock

        Returns:
            QuerySet of Product objects with low stock
        """

        if not info.context.user.is_staff:
            return Product.objects.none()

        return Product.objects.filter(stock__gt=0, stock__lte=threshold)

    def resolve_active_users(
        self, info: graphene.ResolveInfo, days: int = 30
    ) -> QuerySet[User]:
        """
        Resolve active users query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context
            days: Number of days to consider for user activity

        Returns:
            QuerySet of active User objects
        """

        if not info.context.user.is_staff:
            return User.objects.none()

        since_date = timezone.now() - timedelta(days=days)
        return User.objects.filter(
            order_set__created_at__gte=since_date
        ).distinct()

    def resolve_repeat_customers(
        self, info: graphene.ResolveInfo
    ) -> QuerySet[User]:
        """
        Resolve repeat customers query. Only available to staff users.

        Args:
            info: GraphQL resolve info containing request context

        Returns:
            QuerySet of User objects who are repeat customers
        """

        if not info.context.user.is_staff:
            return User.objects.none()

        return User.objects.annotate(order_count=Count("order_set")).filter(
            order_count__gt=1
        )


class CreateProduct(graphene.Mutation):
    """Mutation to create a new product."""

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        description = graphene.String(required=True)

    product = graphene.Field(ProductType)

    def mutate(
        self,
        info: graphene.ResolveInfo,
        name: str,
        price: Decimal,
        description: str,
    ) -> "CreateProduct":
        """
        Create a new product. Only staff users can create products.

        Args:
            info: GraphQL resolve info containing request context
            name: Name of the product
            price: Price of the product
            description: Description of the product

        Returns:
            CreateProduct mutation object with the created product

        Raises:
            Exception: If user is not authorized to create products
        """

        if not info.context.user.is_staff:
            raise Exception("Not authorized to create products")

        product = Product(name=name, price=price, description=description)
        product.save()
        return CreateProduct(product=product)


class Mutation(graphene.ObjectType):
    """Main GraphQL mutation class containing all available mutations."""

    create_product = CreateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
