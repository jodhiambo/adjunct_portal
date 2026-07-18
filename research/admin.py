from django.contrib import admin
from .models import (
    Research,
    ExternalCollaborator,
    Donor,
    Funding,
    ProposalDocument,
    Comment,
)


class FundingInline(admin.TabularInline):
    model = Funding
    extra = 1


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'review_status', 'created_by', 'created_at')
    list_filter = ('status', 'review_status')
    search_fields = ('title', 'description')
    inlines = [FundingInline]


@admin.register(ExternalCollaborator)
class ExternalCollaboratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'institution')
    search_fields = ('name', 'email', 'institution')


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone')
    search_fields = ('name',)


@admin.register(ProposalDocument)
class ProposalDocumentAdmin(admin.ModelAdmin):
    list_display = ('topic', 'research', 'review_status', 'uploaded_by', 'uploaded_at')
    list_filter = ('review_status',)
    search_fields = ('topic',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('research', 'user', 'created_at')