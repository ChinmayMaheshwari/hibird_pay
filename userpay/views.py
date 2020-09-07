from django.shortcuts import render,HttpResponse
from .models import *
from django.http import HttpResponseRedirect
import razorpay
from datetime import datetime,timedelta,date

# Create your views here.
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import *
from .utils import *
from .forms import ContactForm

# API KEYS Enviroment var
RAZORPAY_PUBLICKEY = 'rzp_test_gRPiCKGFiZqfz3'
RAZORPAY_PRIVATEKEY = 'Px4TjJH8yq5bipqdPEILY35a'
client = razorpay.Client(auth=(RAZORPAY_PUBLICKEY,RAZORPAY_PRIVATEKEY))

class SliderView(viewsets.ModelViewSet):
	queryset = Slider.objects.all()
	serializer_class = SliderSerializer
	http_method_names = ['get']	
	permission_classes = [IsAuthenticated]

class PlanView(viewsets.ModelViewSet):
	queryset = PlanDetail.objects.all()
	serializer_class = PlanSerializer
	http_method_names = ['get']	
	permission_classes = [IsAuthenticated]

class TransactionView(viewsets.ModelViewSet):
	queryset = TransactionDetail.objects.all()
	serializer_class = TransactionDetailSerializer
	http_method_names = ['get']	
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user =self.request.user
		print(user.username)
		return self.queryset.filter(user=user).exclude(payment_id=None,cash_payment=True).order_by('-date')

class PersonalInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
    	'current_plan':profile.current_plan.title,
    	'renew_date':profile.due_date.strftime('%d-%b-%Y'),
    	'available':(profile.due_date-date.today()).days,
    	'contact_no':9044046862#Enviroment Variable
    	}
    	return Response(content)

class PaymentInfoView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		user = request.user
		try:
			profile = Profile.objects.get(user=user)
		except:
			return Response({'detail':'Not a Valid User'})

		DATA = {
		'amount':profile.plan_amount*100,
		'currency':'INR',
		'receipt':profile.user.username
		}
		try:
			dic = client.order.create(data=DATA)
			if dic['status']!='created':
				return Response({'detail':'Razorpay Error'})
			transaction = TransactionDetail(user=user,order_id=dic['id'],date=datetime.today(),amount=profile.plan_amount)
			transaction.save()
		except:
			return Response({'detail':'There is some error please try again later'})
		content = {
    	'order':dic['id'],
        'status':'false', 
    	'amount':profile.plan_amount,
    	'transaction':transaction.id,
    	'key':RAZORPAY_PUBLICKEY#os.environ.get('Razorpay_Key')
    	}
		return Response(content)
	
	def post(self,request):
		try:
			id_of_transaction = int(request.data.get('id'))
			transaction = TransactionDetail.objects.get(id=id_of_transaction)
			transaction.date=datetime.now()
			transaction.payment_id = request.data.get('razorpay_payment_id')
		except:
			return Response({'detail':'Please Provide All Data'})
		#client = razorpay.Client(auth=(RAZORPAY_PUBLICKEY,RAZORPAY_PRIVATEKEY))
		try:
			client.utility.verify_payment_signature({'razorpay_order_id':transaction.order_id,'razorpay_payment_id':request.data.get('razorpay_payment_id'),'razorpay_signature':request.data.get('razorpay_signature')})
			transaction.success	=True
			transaction.invoice = 'invoice/'+str(transaction.id)
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
			generateInvoice(request,transaction.id)
			return Response({'transaction':True})
		except:
			return Response({'transaction':False})

def index(request):
	plans = PlanDetail.objects.all()
	enter = Entertainment.objects.all()
	try:
		sliders = WebSlider.objects.all().order_by('-id')[:4]
	except:
		sliders = WebSlider.objects.all()
	return render(request,'index.html',{'plans':plans,'sliders':sliders,'enter':enter})

def about(request):
	return render(request,'about.html')

def profile(request):
	user = request.user
	request.session.set_expiry(6000)
	try:
		profile = Profile.objects.get(user=user)
	except:
		return HttpResponseRedirect('/login/')
	transaction = TransactionDetail.objects.filter(user=user).exclude(payment_id=None,cash_payment=True).order_by('-date')
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
		#client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		try:
			dic = client.order.create(data=DATA)
			transaction = TransactionDetail(user=user,order_id=dic['id'],date=datetime.today(),amount=profile.plan_amount)
			transaction.save()
		except:
			return HttpResponse('Server Error Try Again Later')
		return render(request,'payment.html',{'order':dic['id'],'amount':dic['amount'],'user':profile,'key':'rzp_test_gRPiCKGFiZqfz3','transaction':transaction})

	else:
		data = request.POST
		transaction = TransactionDetail.objects.get(id=request.POST['tran'])
		transaction.date=datetime.now()
		transaction.payment_id = data['razorpay_payment_id']
		#client = razorpay.Client(auth=('rzp_test_gRPiCKGFiZqfz3','Px4TjJH8yq5bipqdPEILY35a'))
		try:
			client.utility.verify_payment_signature({'razorpay_order_id':transaction.order_id,'razorpay_payment_id':data['razorpay_payment_id'],'razorpay_signature':data['razorpay_signature']})
			transaction.success	= True
			transaction.invoice = 'invoice/'+str(transaction.id)
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
			generateInvoice(request,transaction.id)
			return HttpResponseRedirect('/profile/?transaction=success')
		except:
			return HttpResponse('Transaction Failed')


import requests
import uuid	
def generateInvoice(request,tid=None):
	from weasyprint import HTML, CSS
	from django.template.loader import get_template
	token = request.GET.get('token')
	user = request.user
	if token:
		user = Token.objects.get(key=str(token)).user
	if user:
		try:
			transaction = TransactionDetail.objects.get(id=tid,success=True)
		except:
			return HttpResponse('Invalid Transaction')
		if transaction.cash_payment or (transaction.user!=user and not user.is_superuser):
			return HttpResponse('Invalid Transaction')
		user = transaction.user
		profile = Profile.objects.get(user=user)
		data = {
		'id':transaction.id,
		'customer_id':user.username,
		'email':user.email,
		'mobile_no':profile.mobile_no,
		'name':user.first_name+' '+user.last_name,
		'date':transaction.date,
		'due_date':profile.due_date,
		'tran_id':transaction.payment_id,
		'amount':profile.plan_amount-(profile.plan_amount*18)/100,
		'month':transaction.date.strftime('%B'),
		'nine_per':(profile.plan_amount*9)/100,
		'total':profile.plan_amount,
		'gst':profile.gst if profile.gst else 'NA',
		'address':profile.address,
		'amount_words':convertToWords(profile.plan_amount)
		}
		html_template = get_template('invoice2.html').render(data)
		file_name = uuid.uuid1()
		pdf_file = HTML(string=html_template).write_pdf('media/invoice/'+str(file_name)+'.pdf')
		transaction.invoice_file = 'invoice/'+str(file_name)+'.pdf'
		transaction.save()
		message = 'This is a Transaction of '+str(profile.plan_amount)+' RS by '+user.first_name+'. customer id:'+user.username
		r = requests.get('http://smslogin.pcexpert.in/api/mt/SendSMS?user=HIBIRD&password=123456&senderid=INFOSM&channel=Trans&DCS=0&flashsms=0&number='+'7905999153'+'&text='+message+'&route=02')
		print(r.status_code)
		if profile.mobile_no:
			message = 'Your Recharge of '+str(profile.plan_amount)+' RS is Successful Thank You For Being Part of Hibird Broadband'
			r = requests.get('http://smslogin.pcexpert.in/api/mt/SendSMS?user=HIBIRD&password=123456&senderid=INFOSM&channel=Trans&DCS=0&flashsms=0&number='+profile.mobile_no+'&text='+message+'&route=02')
			print(r.status_code)
		# response = HttpResponse(transaction.invoice_file, content_type='application/pdf')
		# response['Content-Disposition'] = 'attachment;filename='+str(transaction.id)+'".pdf"'
		# return response
		# pdf = render_to_pdf('invoice.html',data)
		# if pdf:
		# 	response = HttpResponse(pdf, content_type='application/pdf')
		# 	filename = "Invoice.pdf"
		# 	content = "inline; filename='Invoice.pdf'"
		# 	download = request.GET.get("download")
		# 	if download:
		# 	    content = "attachment; filename='Invoice.pdf'"
		# 	response['Content-Disposition'] = content
		# 	return response
		# return HttpResponse(pdf, content_type='application/pdf')
	else:
		return HttpResponseRedirect('/login/')

def contactForm(request):
	if request.method=="POST":
		try:
			contact = ContactForm(request.POST)
			contact.save()
			return HttpResponseRedirect('/?success=True')
		except:
			pass
	return HttpResponseRedirect('/?fail=True')

from django.contrib.auth.views import PasswordResetView
from django.middleware.csrf import get_token
class ForgotPasswordView(APIView):
	def post(self,request):
		email = request.data.get('email')
		try:
			user = User.objects.get(email=email)
			if user:
				request.data._mutable = True
				request.data['csrfmiddlewaretoken'] = get_token(request)
				request.data._mutable = False
				PasswordResetView.as_view()(request,from_email=email)
				return Response({'status':'send'})
		except:
			return Response({'status':'User Not Found'},status=400)