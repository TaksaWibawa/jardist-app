from django.contrib import admin

class AuditableAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']
    readonly_fields = ['created_at', 'created_by', 'last_updated_at', 'last_updated_by']

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj: 
            return [(None, {'fields': [field for field in fieldsets[0][1]['fields'] if field not in self.readonly_fields]})]
        return fieldsets
