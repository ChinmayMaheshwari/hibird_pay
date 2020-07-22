from django.contrib import admin
from .models import *
from .forms import *
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from django.contrib.admin import SimpleListFilter
from datetime import datetime

class PaidFilter(SimpleListFilter):
    title = 'Bill Paid' # or use _('country') for translated title
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        #countries = set([c.month for c in model_admin.model.objects.all()])
        return [('Not Paid','Not Paid'),]

    def queryset(self, request, queryset):
        if self.value() == 'Not Paid':
            users = TransactionDetail.objects.filter(payment_month=datetime.today().strftime("%B"),success=True).values_list('user__username')
            return User.objects.exclude(username__in=users)

admin.site.register(Profile)

class TransactionAdmin(admin.ModelAdmin):
    search_fields = ('user__username','user__first_name','user__email',)
    list_filter = ('success','payment_month',)

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username','user__email','user__mobile_no',)



admin.site.register(TransactionDetail,TransactionAdmin)
class UserAdmin(UserAdmin):
    add_form = UserCreateForm
    list_filter = (PaidFilter,'is_staff',)
    prepopulated_fields = {'username': ('email' , )}
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username','email', 'password1', 'password2', ),
        }),
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