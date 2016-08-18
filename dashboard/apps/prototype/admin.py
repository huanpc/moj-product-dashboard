import re

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.admin import csrf_protect_m
from django.contrib.auth.decorators import permission_required
from django.core.checks import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from .models import (Person, Rate, Client, Project, Cost, Budget,
                     ProjectStatus, ProjectGroupStatus, Note, ProjectGroup,
                     Saving)
from .forms import (PayrollUploadForm, ExportForm)
from .permissions import ReadOnlyPermissions, FinancePermissions


class ReadOnlyAdmin(ReadOnlyPermissions, admin.ModelAdmin):
    pass


class RateInline(FinancePermissions, admin.TabularInline):
    model = Rate
    extra = 0


class IsCivilServantFilter(admin.SimpleListFilter):
    """
    this filter shows labels of civil servant or contractor
    instead of boolean flags
    """
    title = 'civil servant | contractor'
    parameter_name = 'is_civil_servant'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Civil Servant'),
            ('no', 'Contractor'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_contractor=False)
        elif self.value() == 'no':
            return queryset.filter(is_contractor=True)
        else:
            return queryset


class IsCurrentStaffFilter(admin.SimpleListFilter):
    """
    this filter shows `is_current=True` by default
    """
    title = 'is current staff?'
    parameter_name = 'is_current_staff'

    def lookups(self, request, model_admin):
        return (
            ('all', 'All'),
            (None, 'Yes'),
            ('no', 'No'),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:  # pragma: no cover
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(is_current=True)
        elif self.value() == 'no':
            return queryset.filter(is_current=False)
        else:
            return queryset


class PersonAdmin(ReadOnlyAdmin, FinancePermissions):
    inlines = [RateInline]
    ordering = ('name',)
    list_display = ('name', 'job_title',
                    'contractor_civil_servant', 'is_current')
    search_fields = ('name', 'job_title')
    list_filter = (IsCivilServantFilter, IsCurrentStaffFilter)
    fields = ['name', 'staff_number', 'job_title', 'email',
              'is_contractor', 'is_current']

    def contractor_civil_servant(self, obj):
        if obj.is_contractor:
            return 'Contractor'
        else:
            return 'Civil Servant'
    contractor_civil_servant.short_description = 'Contractor | Civil Servant'

    def get_urls(self):
        urls = [
            url(
                r'^upload/$',
                self.admin_site.admin_view(self.upoload_view),
                name='person_upload_payroll'),
        ]
        return urls + super(PersonAdmin, self).get_urls()

    def has_upload_permission(self, request, obj=None):
        return self.is_finance(request.user)

    def get_model_perms(self, request):
        perms = super(PersonAdmin, self).get_model_perms(request)
        perms.update({
            'upload': self.has_upload_permission(request),
        })
        return perms

    @csrf_protect_m
    @transaction.atomic
    @method_decorator(permission_required('prototype.upload_person',
                                          raise_exception=True))
    def upoload_view(self, request, *args, **kwargs):
        if not self.has_upload_permission(request):
            raise PermissionDenied

        if request.method == 'POST':
            form = PayrollUploadForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save()
                level = messages.INFO
                message = 'Successfully uploaded %s payroll' % form.month
            else:
                level = messages.ERROR
                message = 'Errors uploading %s payroll' % form.month

            self.message_user(request, message, level=level)
        else:
            form = PayrollUploadForm()

        context = self.admin_site.each_context(request)
        context.update({
            'opts': self.model._meta,
            'has_permission': self.has_upload_permission(request),
            'form': form,
        })

        return render_to_response(
            'admin/prototype/upload.html',
            context,
            context_instance=RequestContext(request))


class RateAdmin(FinancePermissions, admin.ModelAdmin):
    search_fields = ('person__name', 'person__job_title')


class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'float_id')
    fields = ['id', 'name', 'float_id', 'visible']
    readonly_fields = ['id', 'name', 'float_id']
    exclude = ['raw_data']


class CostInline(admin.TabularInline):
    model = Cost
    extra = 0


class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 0


class ProjectStatusInline(admin.TabularInline):
    model = ProjectStatus
    extra = 0


class ProjectGroupStatusInline(admin.TabularInline):
    model = ProjectGroupStatus
    extra = 0


class NoteInline(admin.TabularInline):
    model = Note
    extra = 0


class SavingInline(admin.TabularInline):
    model = Saving
    extra = 0


class ProjectAdmin(admin.ModelAdmin, FinancePermissions):
    fields = ['name', 'description', 'float_id', 'is_billable',
              'project_manager', 'client', 'discovery_date', 'alpha_date',
              'beta_date', 'live_date', 'end_date', 'visible']
    exclude = ['raw_data']
    inlines = [CostInline, BudgetInline, SavingInline, ProjectStatusInline,
               NoteInline]
    readonly_fields = ('name', 'description', 'float_id', 'is_billable',
                       'project_manager', 'client')
    list_display = ('name', 'status', 'phase', 'client', 'discovery_date',
                    'budget')
    search_fields = ('name', 'float_id')

    def get_urls(self):
        urls = [
            url(
                r'^export/$',
                self.admin_site.admin_view(self.export_view),
                name='project_export'),
        ]
        return urls + super(ProjectAdmin, self).get_urls()

    @csrf_protect_m
    @transaction.atomic
    @method_decorator(permission_required('prototype.adjustmentexport_project',
                                          raise_exception=True))
    def export_view(self, request):
        if not self.is_finance(request.user):  # pragma: no cover
            raise PermissionDenied

        if request.method == 'POST':
            form = ExportForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                fname = '%s_%s_%s-%s.xlsm' % (
                    form.cleaned_data['export_type'],
                    re.sub(
                        '[^0-9a-zA-Z]+',
                        '-',
                        form.cleaned_data['project'].name),
                    form.cleaned_data['date'].year,
                    form.cleaned_data['date'].month)
                workbook = form.export()
                response = HttpResponse(
                    content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'attachment; filename=%s' \
                                                  % fname
                workbook.save(response)
                return response
        else:
            form = ExportForm()

        context = self.admin_site.each_context(request)
        context.update({
            'opts': self.model._meta,
            'has_permission': self.is_finance(request.user),
            'form': form,
        })

        return render_to_response(
            'admin/prototype/export.html',
            context,
            context_instance=RequestContext(request))


class TaskAdmin(ReadOnlyAdmin):
    search_fields = ('name', 'person__name', 'project__name', 'float_id')
    exclude = ['raw_data']


class ProjectGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('projects', )
    list_display = ('name', 'render_projects')
    inlines = [ProjectGroupStatusInline]

    def render_projects(self, obj):  # pragma: no cover
        return '<br/>'.join([
            '<a href="{}"/>{}</a>'.format(p.admin_url, p.name)
            for p in obj.projects.all()])
    render_projects.short_description = 'Projects'
    render_projects.allow_tags = True


admin.site.register(Person, PersonAdmin)
admin.site.register(Client, ClientAdmin)

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectGroup, ProjectGroupAdmin)
