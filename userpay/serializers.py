from rest_framework import serializers
from .models import *
from datetime import datetime

class TransactionDetailSerializer(serializers.ModelSerializer):
    # invoice = serializers.SerializerMethodField('slug_field')
    # def slug_field(self,obj):
    #     return obj.invoice_file
    date = serializers.SerializerMethodField('format_date')
    def format_date(self,obj):
    	return obj.date.strftime('%I:%M %p  %d-%b-%Y')
    class Meta:
        model = TransactionDetail
        fields = ['order_id','payment_id','date','success','amount','invoice_file',]

class PlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlanDetail
		fields='__all__'
class SliderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Slider
		fields = '__all__'