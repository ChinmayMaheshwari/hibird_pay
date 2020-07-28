from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# from django.contrib.auth.models import User
# from django.dispatch import receiver
# from django.db.models.signals import post_save

class Profile(models.Model):
	def file_path(self,filename):
		return "{0}/{1}/{2}".format('users','document',filename)
	packs = (
		('Browse+ | 12MBPS','Browse+ | 12MBPS'),
		('Pace+ | 20MBPS','Pace+ | 20MBPS'),
		('Quick+ | 50MBPS','Quick+ | 50MBPS'),
		)
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	mobile_no = models.CharField(max_length=10)
	current_plan = models.CharField(max_length=100,choices=packs,default=12)	
	plan_amount = models.PositiveIntegerField()
	address = models.TextField(blank=True,null=True)
	document_no = models.CharField(max_length=20)
	document = models.FileField(upload_to = file_path)

	def __str__(self):
		return self.user.username

class TransactionDetail(models.Model):
	month = (
		('January','January'),
		('February','February'),
		('March','March'),
		('April','April'),
		('May','May'),
		('June','June'),
		('July','July'),
		('August','August'),
		('September','September'),
		('Octomber','Octomber'),
		('November','November'),
		('December','December')
		)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	order_id = models.CharField(max_length=50)
	payment_id = models.CharField(max_length=50,blank=True,null=True)
	date = models.DateTimeField(null=True,blank=True)
	payment_month = models.CharField(max_length=10,choices=month)
	success = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username
# @receiver(post_save,sender=User)
# def username_generation(sender,**kwargs):
# 	if kwargs.get('created'):
# 		instance = kwargs.get('instance')
# 		instance.username = 'Hybrid'+str(instance.id)
# 		instance.save()

class PlanDetail(models.Model):
	title = models.CharField(max_length=50)
	amount = models.PositiveIntegerField()
	description = models.TextField()
	photo = models.FileField(null=True,blank=True,upload_to='plan/')

	def __str__(self):
		return self.title

class Slider(models.Model):
	title = models.CharField(max_length=50)
	photo = models.FileField(upload_to='slider/')

	def __str__(self):
		return self.title