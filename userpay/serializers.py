from rest_framework import serializers
from .models import *

class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetail
        fields = ['order_id','payment_id','date','payment_month','success',]

class PlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlanDetail
		fields='__all__'
class SliderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Slider
		fields = '__all__'