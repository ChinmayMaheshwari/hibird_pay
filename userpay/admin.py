from django.contrib import admin
from .models import *
from .forms import *
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from django.contrib.admin import SimpleListFilter
from datetime import datetime,date,timedelta
from django.utils.html import format_html
import requests
from zipfile import ZipFile
from io import BytesIO
from django.http import HttpResponse
#from wsgiref.util import FileWrapper

class PaidFilter(SimpleListFilter):
    title = 'Bill Paid'
    parameter_name = 'due_date'

    def lookups(self, request, model_admin):
        return [('Not Paid','Not Paid'),]

    def queryset(self, request, queryset):
        if self.value() == 'Not Paid':
            return Profile.objects.filter(due_date__lte=date.today())


class TransactionAdmin(admin.ModelAdmin):
    search_fields = ('user__username','user__first_name','user__email',)
    list_filter = ('success','cash_payment',)
    actions = ['download_all_invoice',]
    def download_all_invoice(self,request,queryset):
        buffer= BytesIO()
        zipObj= ZipFile( buffer, "w" )
        for i in queryset:
            try:
                zipObj.write('media/'+str(i.invoice_file))
            except:
                pass
        zipObj.close()
        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=invoices.zip'
        return response
    # exclude = ('invoice',)
    # readonly_fields = ('my_clickable_link',)
    # def my_clickable_link(self, instance):
    #     return format_html(
    #         '<a href="/{0}">Click Here to Download Invoice</a>',
    #         instance.invoice,
    #         instance.invoice,
    #     )

    # my_clickable_link.short_description = "Download Invoice"
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username','user__email','mobile_no',)
    readonly_fields = ('due_date',)
    list_filter = (PaidFilter,)
    actions = ['send_remider',]
    autocomplete_fields = ['user',]
    def send_remider(self,request,queryset):
        from django.core.mail import send_mail
        users = Profile.objects.filter(due_date__lte=date.today()+timedelta(days=3))
        mobile = []
        for i in users:
            message = 'Hello '+i.user.first_name+',This is to remind you your wifi services are going to expire on '+str(i.due_date)+' please pay your due to enjoy our services. use https://hybird.herokuapp.com for paying your dues'
            if i.user.email:
                try:
                    send_mail('Hibird Payment Reminder',message,'chinmay1305@gmail.com',[i.user.email,])
                except:
                    pass 
            if i.mobile_no:
                r = requests.get('http://smslogin.pcexpert.in/api/mt/SendSMS?user=HIBIRD&password=123456&senderid=INFOSM&channel=Trans&DCS=0&flashsms=0&number='+i.mobile_no+'&text='+message+'&route=02')
                print(r.status_code)

admin.site.register(Profile,ProfileAdmin)
admin.site.register(TransactionDetail,TransactionAdmin)

class UserAdmin(UserAdmin):
    add_form = UserCreateForm
    list_filter = ('is_staff',)
    prepopulated_fields = {'username': ('email' , )}
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username','email', 'password1', 'password2', ),
        }),
    )
    list_display = ('customer_id',)
    def customer_id(self,obj):
        return obj.username
    customer_id.short_description = 'Customer Id'
    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs['labels'] = {'username': 'Customer Id'}
        return super().get_form(request, obj=obj, change=change, **kwargs)
    def change_view(self, request, object_id):

        # we want to limit the ability of the normal user to edit permissions.
        if request.user.is_superuser:
            self.fieldsets = (
                (None, {'fields': ('username', 'password')}),
                (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','groups')}),
                (('Important dates'), {'fields': ('last_login', 'date_joined')}),
             #   (('Groups'), {'fields': ('groups',)}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('username',)}),
                (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                #(('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
                #(('Important dates'), {'fields': ('last_login', 'date_joined')}),
                #(('Groups'), {'fields': ('groups',)}),
            )


        return super(UserAdmin, self).change_view(request, object_id,
            )
    def save_model(self, request, obj, form, change):
        if not change and (not form.cleaned_data['password1'] or not obj.has_usable_password()):
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string())
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)

        if reset_password:
            reset_form = PasswordResetForm({'email': obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                request=request,
                use_https=request.is_secure(),
                # subject_template_name='registration/account_creation_subject.txt',
                # email_template_name='registration/account_creation_email.html',
            )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(PlanDetail)
admin.site.register(Slider)
admin.site.register(WebSlider)
admin.site.register(Entertainment)
admin.site.register(ContactFormData)
admin.site.site_header = "Hibird Panel"
admin.site.site_title = "Hibird "