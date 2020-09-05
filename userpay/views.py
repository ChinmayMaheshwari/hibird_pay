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
from .utils import render_to_pdf
from .forms import ContactForm

# API KEYS Enviroment var
RAZORPAY_PUBLICKEY = 'rzp_test_gRPiCKGFiZqfz3'
RAZORPAY_PRIVATEKEY = 'Px4TjJH8yq5bipqdPEILY35a'
client = razorpay.Client(auth=(RAZORPAY_PUBLICKEY,RAZORPAY_PRIVATEKEY))

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
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
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
			profile = Profile.objects.get(user=request.user)
			profile.due_date = profile.due_date+timedelta(days=30)
			profile.save()
			transaction.save()
			return HttpResponseRedirect('/profile/?transaction=success')
		except:
			return HttpResponse('Transaction Failed')



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
		'month':profile.due_date.strftime('%B'),
		'nine_per':(profile.plan_amount*9)/100,
		'total':profile.plan_amount,
		'gst':profile.gst if profile.gst else 'NA'
		}
		html_template = get_template('invoice2.html').render(data)
		pdf_file = HTML(string=html_template).write_pdf()
		response = HttpResponse(pdf_file, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment;filename='+str(transaction.id)+'".pdf"'
		return response
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

