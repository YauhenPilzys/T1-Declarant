from django.contrib import admin
from .models import TreeTnved, Tnved, DeclarantOrgInfo, UserOrg
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

admin.site.register(TreeTnved)
admin.site.register(Tnved)
admin.site.register(DeclarantOrgInfo)

class UserOrgInline(admin.StackedInline):
    model = UserOrg
    can_delete = False
    verbose_name_plural = 'Таможенный представитель (информация для заполнения)'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserOrgInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


