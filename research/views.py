from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import timedelta

from .models import Research, ProposalDocument, Donor, Funding
from .forms import ResearchForm, FundingFormSet, ProposalDocumentForm, CommentForm, ReviewForm
from accounts.models import ResearcherProfile
from accounts.utils import create_notification


def is_staff(user):
    return user.is_staff


@login_required
def research_list_view(request):
    researches = Research.objects.filter(review_status='approved').order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        researches = researches.filter(status=status_filter)

    return render(request, 'research/research_list.html', {
        'researches': researches,
        'status_filter': status_filter,
    })


@login_required
def research_detail_view(request, pk):
    research = get_object_or_404(Research, pk=pk)

    is_owner_or_staff = request.user == research.created_by or request.user.is_staff

    # Non-approved entries are only visible to their creator or staff
    if research.review_status != 'approved' and not is_owner_or_staff:
        messages.error(request, 'This research entry is not yet available.')
        return redirect('research_list')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.research = research
            comment.user = request.user
            comment.save()
            return redirect('research_detail', pk=pk)
    else:
        comment_form = CommentForm()

    proposal_documents = research.proposal_documents.all() if is_owner_or_staff \
        else research.proposal_documents.filter(review_status='approved')

    return render(request, 'research/research_detail.html', {
        'research': research,
        'comment_form': comment_form,
        'proposal_documents': proposal_documents,
        'is_owner_or_staff': is_owner_or_staff,
    })


@login_required
def research_create_view(request):
    if request.method == 'POST':
        form = ResearchForm(request.POST)
        if form.is_valid():
            research = form.save(commit=False)
            research.created_by = request.user
            research.review_status = 'pending'
            research.save()
            form.save_m2m()

            funding_formset = FundingFormSet(request.POST, instance=research)
            if funding_formset.is_valid():
                funding_formset.save()

            messages.success(request, 'Research entry submitted for admin review.')
            return redirect('research_detail', pk=research.pk)
    else:
        form = ResearchForm()
        funding_formset = FundingFormSet()

    return render(request, 'research/research_form.html', {
        'form': form,
        'funding_formset': funding_formset,
    })


@login_required
def research_edit_view(request, pk):
    research = get_object_or_404(Research, pk=pk)

    if request.user != research.created_by and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this entry.")
        return redirect('research_detail', pk=pk)

    if request.method == 'POST':
        form = ResearchForm(request.POST, instance=research)
        funding_formset = FundingFormSet(request.POST, instance=research)

        if form.is_valid() and funding_formset.is_valid():
            research = form.save(commit=False)
            research.review_status = 'pending'  # send back for re-review after edits
            research.save()
            form.save_m2m()
            funding_formset.save()

            messages.success(request, 'Updated and resubmitted for review.')
            return redirect('research_detail', pk=pk)
    else:
        form = ResearchForm(instance=research)
        funding_formset = FundingFormSet(instance=research)

    return render(request, 'research/research_form.html', {
        'form': form,
        'funding_formset': funding_formset,
    })


@login_required
def proposal_upload_view(request, pk):
    research = get_object_or_404(Research, pk=pk)

    if request.method == 'POST':
        form = ProposalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.research = research
            proposal.uploaded_by = request.user
            proposal.review_status = 'pending'
            proposal.save()

            messages.success(request, 'Proposal document submitted for review.')
            return redirect('research_detail', pk=pk)
    else:
        form = ProposalDocumentForm()

    return render(request, 'research/proposal_form.html', {
        'form': form,
        'research': research,
    })


# --- Admin/staff review ---

@user_passes_test(is_staff)
def review_queue_view(request):
    pending_research = Research.objects.filter(review_status='pending')
    pending_proposals = ProposalDocument.objects.filter(review_status='pending')

    return render(request, 'research/review_queue.html', {
        'pending_research': pending_research,
        'pending_proposals': pending_proposals,
        'review_form': ReviewForm(),
    })


@user_passes_test(is_staff)
def review_research_action_view(request, pk):
    research = get_object_or_404(Research, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            comment = form.cleaned_data['comment']

            research.review_status = action
            research.review_comment = comment
            research.reviewed_by = request.user
            research.reviewed_at = timezone.now()
            research.save()

            action_messages = {
                'approved': 'Your research entry has been approved and is now live.',
                'needs_revision': 'Your research entry needs revision — check the reviewer comment.',
                'flagged': 'Your research entry has been flagged as inappropriate.',
            }

            if research.created_by:
                create_notification(
                    research.created_by,
                    action_messages[action],
                    link=f'/research/{research.pk}/'
                )

            messages.success(request, 'Review submitted.')

    return redirect('review_queue')


@user_passes_test(is_staff)
def review_proposal_action_view(request, pk):
    proposal = get_object_or_404(ProposalDocument, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            comment = form.cleaned_data['comment']

            proposal.review_status = action
            proposal.review_comment = comment
            proposal.reviewed_by = request.user
            proposal.reviewed_at = timezone.now()
            proposal.save()

            action_messages = {
                'approved': 'Your proposal document has been approved and is now visible.',
                'needs_revision': 'Your proposal document needs revision — check the reviewer comment.',
                'flagged': 'Your proposal document has been flagged as inappropriate.',
            }

            if proposal.uploaded_by:
                create_notification(
                    proposal.uploaded_by,
                    action_messages[action],
                    link=f'/research/{proposal.research.pk}/'
                )

            messages.success(request, 'Review submitted.')

    return redirect('review_queue')


# --- Dashboards ---
@user_passes_test(is_staff)
def analytics_dashboard_view(request):
    approved_research = Research.objects.filter(review_status='approved')

    total_research = approved_research.count()

    by_status = approved_research.values('status').annotate(count=Count('id')).order_by('status')
    status_labels = [dict(Research.STATUS_CHOICES).get(item['status'], item['status']) for item in by_status]
    status_counts = [item['count'] for item in by_status]

    active_researchers = ResearcherProfile.objects.filter(
        research_works__status__in=['won', 'ongoing'],
        research_works__review_status='approved'
    ).distinct()

    dormant_researchers = ResearcherProfile.objects.exclude(
        id__in=active_researchers.values_list('id', flat=True)
    )

    active_count = active_researchers.count()
    dormant_count = dormant_researchers.count()

    funding_totals = Funding.objects.aggregate(
        total_min=Sum('amount_min'),
        total_max=Sum('amount_max')
    )

    top_donors = Donor.objects.annotate(
        total_funding=Sum('funding__amount_max')
    ).exclude(total_funding__isnull=True).order_by('-total_funding')[:5]

    donor_labels = [d.name for d in top_donors]
    donor_amounts = [float(d.total_funding) for d in top_donors]

    # --- Research submissions trend, adjustable period ---
    PERIOD_CHOICES = [3, 6, 12, 24]
    period_param = request.GET.get('months', '6')

    if period_param == 'all':
        selected_period = 'all'
        trend_queryset = approved_research
    else:
        try:
            months_int = int(period_param)
        except (TypeError, ValueError):
            months_int = 6
        if months_int not in PERIOD_CHOICES:
            months_int = 6
        selected_period = months_int
        # Approximation: 30 days/month, close enough for a recent-activity trend view
        start_date = timezone.now() - timedelta(days=30 * months_int)
        trend_queryset = approved_research.filter(created_at__gte=start_date)

    monthly_trend = (
        trend_queryset
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    trend_labels = [item['month'].strftime('%b %Y') for item in monthly_trend]
    trend_counts = [item['count'] for item in monthly_trend]

    top_researchers = ResearcherProfile.objects.order_by('-proposals_won')[:5]

    pending_research_count = Research.objects.filter(review_status='pending').count()
    pending_proposal_count = ProposalDocument.objects.filter(review_status='pending').count()

    recent_research = Research.objects.order_by('-created_at')[:5]
    recent_proposals = ProposalDocument.objects.order_by('-uploaded_at')[:5]

    context = {
        'total_research': total_research,
        'active_count': active_count,
        'dormant_count': dormant_count,
        'funding_totals': funding_totals,
        'top_donors': top_donors,
        'top_researchers': top_researchers,
        'pending_research_count': pending_research_count,
        'pending_proposal_count': pending_proposal_count,
        'recent_research': recent_research,
        'recent_proposals': recent_proposals,
        'selected_period': selected_period,
        'period_choices': PERIOD_CHOICES,

        'status_labels': status_labels,
        'status_counts': status_counts,
        'donor_labels': donor_labels,
        'donor_amounts': donor_amounts,
        'trend_labels': trend_labels,
        'trend_counts': trend_counts,
        'active_dormant_counts': [active_count, dormant_count],
    }

    return render(request, 'research/analytics_dashboard.html', context)

@login_required
def team_finder_view(request):
    """Researcher-facing: browse research that's applied/ongoing to find a team to join."""
    researches = Research.objects.filter(
        review_status='approved',
        status__in=['applied', 'ongoing']
    ).order_by('-created_at')

    return render(request, 'research/team_finder.html', {
        'researches': researches,
    })