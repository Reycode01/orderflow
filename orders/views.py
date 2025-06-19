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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'kitchen':
            return Order.objects.all()
        elif user.role == 'waitstaff':
            return Order.objects.filter(created_by=user)
        return Order.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsWaitstaff()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsKitchenStaff() | IsAdminUser()]
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
        # Get latest unserved order for that table
        order = table.orders.filter(status__in=['pending', 'preparing', 'served', 'delayed']).latest('timestamp')
        serializer = OrderSerializer(order)
        return Response({
            "table": table.number,
            "order": serializer.data
        })
    except Table.DoesNotExist:
        return Response({"error": "Invalid QR Code"}, status=status.HTTP_404_NOT_FOUND)
    except Order.DoesNotExist:
        return Response({"error": "No active order found"}, status=status.HTTP_404_NOT_FOUND)