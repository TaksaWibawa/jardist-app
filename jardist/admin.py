from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from jardist.forms.admin_form import UserAdminForm
from .models import Department, Role, SPK, PK, UserProfile, PKStatusAudit

class AuditableAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']
    readonly_fields = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj: 
            return [(None, {'fields': [field for field in fieldsets[0][1]['fields'] if field not in self.readonly_fields]})]
        return fieldsets
    
class GroupAdmin(DefaultGroupAdmin):
    list_display = ('name', 'get_user_count')

    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = 'Jumlah Pengguna'
    
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Pengguna'
    fk_name = 'user'

class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)
    add_form = UserAdminForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'department'),
        }),
    )
    list_display = ('username', 'get_role', 'get_department', 'is_staff', 'is_superuser', 'get_created_at',
                    'get_created_by', 'get_last_updated_at', 'get_last_updated_by')
                    
    
    def get_created_at(self, obj):
        return obj.userprofile.created_at
    get_created_at.short_description = 'Created At'

    def get_created_by(self, obj):
        return obj.userprofile.created_by
    get_created_by.short_description = 'Created By'

    def get_last_updated_at(self, obj):
        return obj.userprofile.last_updated_at
    get_last_updated_at.short_description = 'Last Updated At'

    def get_last_updated_by(self, obj):
        return obj.userprofile.last_updated_by
    get_last_updated_by.short_description = 'Last Updated By'

    def get_role(self, obj):
        return obj.userprofile.role
    get_role.short_description = 'Role'

    def get_department(self, obj):
        return obj.userprofile.department
    get_department.short_description = 'Department'

    def save_model(self, request, obj, form, change):
        if not change:
            password = form.cleaned_data.get('password1')
            obj.set_password(password)
            print(obj)
        super().save_model(request, obj, form, change)
        role = form.cleaned_data.get('role')
        department = form.cleaned_data.get('department')
        UserProfile.objects.update_or_create(user=obj, defaults={'role': role, 'department': department})
        
        if role:
            group, created = Group.objects.get_or_create(name__iexact=role.name)
            obj.groups.add(group)

class DepartmentAdmin(AuditableAdmin):
    list_display = ['name', 'description'] + AuditableAdmin.list_display

class RoleAdmin(AuditableAdmin):
    list_display = ['name'] + AuditableAdmin.list_display

class SPKAdmin(AuditableAdmin):
    list_display = ['spk_number', 'start_date', 'end_date', 'execution_time', 'maintenance_time', 'department', 'is_without_pk'] + AuditableAdmin.list_display
    readonly_fields = AuditableAdmin.readonly_fields

class PKAdmin(AuditableAdmin):
    list_display = ['pk_number', 'spk', 'start_date', 'end_date', 'execution_time', 'maintenance_time'] + AuditableAdmin.list_display
    readonly_fields = AuditableAdmin.readonly_fields

class PKStatusAuditAdmin(admin.ModelAdmin):
    list_display = ['pk_instance', 'old_status', 'new_status', 'created_at', 'created_by']
    readonly_fields = ['created_at', 'created_by']

    search_fields = ['pk_instance__pk_number']
    list_filter = ['old_status', 'new_status']
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(SPK, SPKAdmin)
admin.site.register(PK, PKAdmin)
admin.site.register(PKStatusAudit, PKStatusAuditAdmin)