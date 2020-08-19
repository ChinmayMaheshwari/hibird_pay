from rest_framework import serializers
from .models import *

class TransactionDetailSerializer(serializers.ModelSerializer):
    invoice = serializers.SerializerMethodField('slug_field')
    def slug_field(self,obj):
        return 'https://hybird.herokuapp.com/invoice/'+str(obj.id)
    class Meta:
        model = TransactionDetail
        fields = ['order_id','payment_id','date','success','amount','invoice',]

class PlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlanDetail
		fields='__all__'
class SliderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Slider
		fields = '__all__'