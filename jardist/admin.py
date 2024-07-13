from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from django.contrib.auth.models import Group, User
from django.db.models import Count
from jardist.forms.admin_form import UserAdminForm

from jardist.models.contract_models import SPK, PK, PKStatusAudit, PKArchiveDocument, Document
from jardist.models.role_models import Department, Role
from jardist.models.task_models import Task, TaskType, SubTask, SubTaskType, SubTaskMaterial, TemplateRAB, TaskDocumentation, TaskDocumentationPhoto
from jardist.models.user_models import UserProfile
from jardist.models.material_models import Material, MaterialCategory

# Auditable Admin
class AuditableAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']
    readonly_fields = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj: 
            return [(None, {'fields': [field for field in fieldsets[0][1]['fields'] if field not in self.readonly_fields]})]
        return fieldsets

# User and Group Admin
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

    fields = ['role', 'department', 'created_at', 'created_by', 'last_updated_at', 'last_updated_by']

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
        super().save_model(request, obj, form, change)
        role = form.cleaned_data.get('role')
        department = form.cleaned_data.get('department')
        UserProfile.objects.update_or_create(user=obj, defaults={'role': role, 'department': department})
        
        if role:
            group, created = Group.objects.get_or_create(name__iexact=role.name)
            obj.groups.add(group)

# Role and Department Admin
class DepartmentAdmin(AuditableAdmin):
    list_display = ['name', 'description'] + AuditableAdmin.list_display

class RoleAdmin(AuditableAdmin):
    list_display = ['name'] + AuditableAdmin.list_display

# Contract Models Admin
class PKInline(admin.TabularInline):
    model = PK
    extra = 1

class SPKAdmin(AuditableAdmin):
    list_display = ['spk_number', 'start_date', 'end_date', 'execution_time', 'maintenance_time', 'department', 'is_without_pk'] + AuditableAdmin.list_display
    inlines = [PKInline]

class PKStatusAuditAdmin(AuditableAdmin):
    list_display = ['pk_instance', 'old_status', 'new_status'] + AuditableAdmin.list_display
    search_fields = ['pk_instance__pk_number']
    list_filter = ['old_status', 'new_status']
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('pickup_file', 'pickup_description', 'proof_file', 'proof_description', 'created_at')

class PkArchiveDocumentAdmin(admin.ModelAdmin):
    list_display = ['pk_instance', 'documents_count'] + AuditableAdmin.list_display

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
            documents_count=Count('documents')
        )
        return queryset

    def documents_count(self, obj):
        return obj.documents_count
    documents_count.admin_order_field = 'documents_count'
    documents_count.short_description = 'Jumlah Arsip Dokumen'

    inlines = [DocumentInline]
    
# Material Models Admin
class MaterialCategoryAdmin(AuditableAdmin):
    list_display = ['name'] + AuditableAdmin.list_display

class MaterialAdmin(AuditableAdmin):
    list_display = ['name', 'unit'] + AuditableAdmin.list_display

# Task Models Admin
class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0

class SubTaskMaterialInline(admin.TabularInline):
    model = SubTaskMaterial
    extra = 0

class TaskTypeAdmin(AuditableAdmin):
    list_display = ['name', 'description'] + AuditableAdmin.list_display

class SubTaskTypeAdmin(AuditableAdmin):
    list_display = ['name', 'description'] + AuditableAdmin.list_display

class TaskAdmin(AuditableAdmin):
    list_display = ['task_name', 'pk_instance', 'task_type', 'customer_name', 'location', 'execution_time', 'maintenance_time', 'status'] + AuditableAdmin.list_display
    inlines = [SubTaskInline]

class SubTaskAdmin(AuditableAdmin):
    list_display = ['sub_task_type', 'task'] + AuditableAdmin.list_display
    inlines = [SubTaskMaterialInline]

class TemplateRABAdmin(AuditableAdmin):
    list_display = ['task_type', 'rab'] + AuditableAdmin.list_display

class TaskDocumentationPhotoInline(admin.TabularInline):
    model = TaskDocumentationPhoto
    extra = 1
    readonly_fields = ['created_at']
    fields = ['photo', 'description', 'created_at']

class TaskDocumentationAdmin(AuditableAdmin):
    list_display = ['get_task_pk', 'documentation_count', 'task', 'location'] + AuditableAdmin.list_display
    inlines = [TaskDocumentationPhotoInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
            documentation_count=Count('photos')
        )
        return queryset
    
    def documentation_count(self, obj):
        return obj.documentation_count
    documentation_count.admin_order_field = 'documentation_count'
    documentation_count.short_description = 'Jumlah Dokumentasi'

    def get_task_pk(self, obj):
        return obj.task.pk_instance.pk_number
    get_task_pk.admin_order_field = 'task__pk_instance__pk_number'
    get_task_pk.short_description = 'No. PK'

# Unregister Default User and Group Admin
admin.site.unregister(User)
admin.site.unregister(Group)

# Authorization Models
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Role, RoleAdmin)

# Contract Models
admin.site.register(SPK, SPKAdmin)
admin.site.register(PKStatusAudit, PKStatusAuditAdmin)
admin.site.register(PKArchiveDocument, PkArchiveDocumentAdmin)

# Material Models
admin.site.register(MaterialCategory, MaterialCategoryAdmin)
admin.site.register(Material, MaterialAdmin)

# Task Models
admin.site.register(TaskType, TaskTypeAdmin)
admin.site.register(SubTaskType, SubTaskTypeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)
admin.site.register(TemplateRAB, TemplateRABAdmin)
admin.site.register(TaskDocumentation, TaskDocumentationAdmin)