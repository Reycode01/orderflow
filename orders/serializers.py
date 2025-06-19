from rest_framework import serializers
from .models import Table, Order

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    delay_status = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'
