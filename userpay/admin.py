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

import requests

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
    list_filter = ('success',)

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
            message = 'Hello '+i.user.first_name+',This is to remind you your wifi services are going to expire on '+str(i.due_date)+' please pay your due to continue our services. use https://hybird.herokuapp.com for paying your dues'
            if i.user.email:
                send_mail('Hibird Payment Remider',message,'chinmay1305@gmail.com',[i.user.email,]) 
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
admin.site.site_header = "Hibird Panel"
admin.site.site_title = "Hibird "