from rest_framework import viewsets
from .models import Order, Table
from .serializers import OrderSerializer, TableSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsWaitstaff, IsKitchenStaff, IsAdminUser


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-timestamp')
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'kitchen':
            return Order.objects.all()
        elif hasattr(user, 'role') and user.role == 'waitstaff':
            return Order.objects.filter(created_by=user)
        return Order.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        user = self.request.user

        if not user.is_authenticated:
            return [IsAuthenticated()]  # Will return 401 if not logged in

        if self.action == 'create':
            return [IsAuthenticated(), IsWaitstaff()]
        elif self.action in ['list', 'retrieve']:
            if hasattr(user, 'role') and (user.role == 'kitchen' or user.is_staff):
                return [IsAuthenticated()]
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]

        return [IsAuthenticated()]


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


@api_view(['GET'])
def qr_confirmation(request, qr_code):
    try:
        table = Table.objects.get(qr_code=qr_code)
        order = table.orders.filter(
            status__in=['pending', 'preparing', 'served', 'delayed']
        ).latest('timestamp')
        serializer = OrderSerializer(order)
        return Response({
            "table": table.number,
            "order": serializer.data
        })
    except Table.DoesNotExist:
        return Response({"error": "Invalid QR Code"}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({"error": "No active order found"}, status=status.HTTP_404_NOT_FOUND)
