from django.contrib import admin

from .models import Application, Company, Status

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant', 'company', 'position', 'location', 'status', 'date_created', 'last_updated', 'job_post',)
    list_filter = ('applicant', 'company', 'location',)
    search_fields = ('company', 'position')
    ordering = ('date_created', 'last_updated')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'created_by')
    list_filter = ('name', 'created_by', 'is_default')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_email')
    search_fields = ('name',)


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Company, CompanyAdmin)