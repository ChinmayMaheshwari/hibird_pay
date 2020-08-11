from django.shortcuts import render,HttpResponse
from .models import *
from django.http import HttpResponseRedirect
import razorpay
from datetime import datetime,timedelta,date

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import *
from .utils import render_to_pdf

class SliderView(viewsets.ModelViewSet):
	queryset = Slider.objects.all()
	serializer_class = SliderSerializer
	http_method_names = ['get']	

class PlanView(viewsets.ModelViewSet):
	queryset = PlanDetail.objects.all()
	serializer_class = PlanSerializer
	http_method_names = ['get']	

class TransactionView(viewsets.ModelViewSet):
	queryset = TransactionDetail.objects.all()
	serializer_class = TransactionDetailSerializer
	http_method_names = ['get']	
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user =self.request.user
		print(user.username)
		return self.queryset.filter(user=user)

class PersonalInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
    	user = request.user
    	try:
    		profile = Profile.objects.get(user=user)
    	except:
    		return Response({'detail':'Not a Valid User'})
    	content = {
        'username': user.username,  
        'first_name': user.first_name,  
    	'last_name': user.last_name,  
    	'email': user.email,  
    	'mobile_no': profile.mobile_no,
    	'amount':profile.plan_amount,  
    	'current_plan':profile.current_plan,
    	'renew_date':profile.due_date,
    	'available':(profile.due_date-date.today()).days
    	}
    	return Response(content)

class PaymentInfoView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, format=None):
		user = request.user
		profile = Profile.objects.get(user=user)
		DATA = {
		'amount':profile.plan_amount*100,
		'currency':'INR',
		'receipt':profile.user.username
		}
		client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		dic = client.order.create(data=DATA)
		try:
			transaction = TransactionDetail(user=user,order_id=dic['id'])
			transaction.save()
		except:
			pass
		content = {
    	'order':dic['id'],
        'status':'false', 
    	'amount':profile.plan_amount,
    	'transaction':transaction.id,
    	'key':'rzp_test_gRPiCKGFiZqfz3'
    	}
		return Response(content)
	
	def post(self,request):
		id_of_transaction = int(request.data.get('id'))
		transaction = TransactionDetail.objects.get(id=id_of_transaction)
		transaction.date=datetime.now()
		transaction.payment_id = request.data.get('razorpay_payment_id')
		client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		try:
			client.utility.verify_payment_signature({'razorpay_order_id':transaction.order_id,'razorpay_payment_id':request.data.get('razorpay_payment_id'),'razorpay_signature':request.data.get('razorpay_signature')})
			transaction.success	=True
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
			return Response({'transaction':True})
		except:
			return Response({'transaction':False})

def index(request):
	plan = PlanDetail.objects.all()
	return render(request,'index.html',{'plan':plan})

def about(request):
	return render(request,'about.html')

def profile(request):
	user = request.user
	try:
		profile = Profile.objects.get(user=user)
	except:
		return HttpResponseRedirect('/login/')
	transaction = TransactionDetail.objects.filter(user=user).order_by('-date')
	return render(request,'profile.html',{'user':user,'profile':profile,'transaction':transaction,'available':(profile.due_date-date.today()).days})

def payment(request):
	if request.method=='GET':
		user  = request.user
		try:
			profile = Profile.objects.get(user=user)
		except:
			return HttpResponseRedirect('/login/')

		DATA = {
		'amount':profile.plan_amount*100,
		'currency':'INR',
		'receipt':profile.user.username
		}
		client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		dic = client.order.create(data=DATA)
		try:
			transaction = TransactionDetail(user=user,order_id=dic['id'])
			transaction.save()
		except:
			pass
		return render(request,'payment.html',{'order':dic['id'],'amount':dic['amount'],'user':profile,'key':'rzp_test_gRPiCKGFiZqfz3','transaction':transaction})

	else:
		data = request.POST
		transaction = TransactionDetail.objects.get(id=request.POST['tran'])
		transaction.date=datetime.now()
		transaction.payment_id = data['razorpay_payment_id']
		client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		try:
			client.utility.verify_payment_signature({'razorpay_order_id':transaction.order_id,'razorpay_payment_id':data['razorpay_payment_id'],'razorpay_signature':data['razorpay_signature']})
			transaction.success	=True
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
			return HttpResponseRedirect('/profile/')
		except:
			return HttpResponse('Transaction Failed')

def generateInvoice(request,tid=None):
	if request.user:
		try:
			transaction = TransactionDetail.objects.get(id=tid,success=True)
		except:
			return HttpResponse('Invalid Transaction')
		user = request.user
		profile = Profile.objects.get(user=user)
		data = {
		'customer_id':user.username,
		'email':user.email,
		'mobile_no':profile.mobile_no,
		'name':user.first_name,
		'date':transaction.date,
		'due_date':profile.due_date,
		'tran_id':transaction.payment_id,
		'amount':profile.plan_amount,
		'month':profile.due_date.strftime('%B')
		}
		pdf = render_to_pdf('invoice.html',data)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "Invoice.pdf"
			content = "inline; filename='Invoice.pdf'"
			download = request.GET.get("download")
			if download:
			    content = "attachment; filename='Invoice.pdf'"
			response['Content-Disposition'] = content
			return response
		# return HttpResponse(pdf, content_type='application/pdf')
	else:
		return HttpResponseRedirect('/login/')