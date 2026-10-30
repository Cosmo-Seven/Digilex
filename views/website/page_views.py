from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from core.models import (
    BookmarkModel,
    ChapterModel,
    LawModel,
    SearchHistoryModel,
    SectionModel,
    UserHistoryModel,
)
import json
import os
import re
import html as html_lib
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def require_law_access(request, law):
    if law.is_free:
        return None
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active or not request.user.is_verified:
        messages.warning(request, "Please complete your payment and wait for admin approval to access this content.")
        return redirect("/")
    return None


def save_user_history(request, law=None, chapter=None, section=None):
    if not request.user.is_authenticated:
        return

    if law is not None:
        UserHistoryModel.objects.update_or_create(
            user=request.user,
            law=law,
        )

    if chapter is not None:
        UserHistoryModel.objects.update_or_create(
            user=request.user,
            chapter=chapter,
        )

    if section is not None:
        UserHistoryModel.objects.update_or_create(
            user=request.user,
            section=section,
        )


def index(request):
    laws = LawModel.objects.all()
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = SearchHistoryModel.objects.filter(
            user=request.user
        ).order_by("-updated_at")[:5]
    context = {
        'laws': laws,
        'recent_searches': recent_searches,
    }
    return render(request, "website/index.html", context)


def chapter(request, law_id):
    law = get_object_or_404(LawModel, id=law_id)
    redirect_to_login = require_law_access(request, law)
    if redirect_to_login:
        return redirect_to_login

    save_user_history(request, law=law)

    search_query = request.GET.get('q', '').strip()
    section_results = SectionModel.objects.none()
    chapters = law.chapters.all().order_by('order')

    if search_query:
        if request.user.is_authenticated and (
            request.GET.get('ajax') != '1' or request.GET.get('save_history') == '1'
        ):
            search, created = SearchHistoryModel.objects.get_or_create(
                user=request.user,
                query=search_query,
            )
            if not created:
                search.updated_at = now()
                search.save(update_fields=('updated_at',))

        chapters = chapters.filter(
            Q(chapter_number__icontains=search_query)
            | Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sections__section_number__icontains=search_query)
            | Q(sections__title__icontains=search_query)
            | Q(sections__offense__icontains=search_query)
            | Q(sections__penalty__icontains=search_query)
        ).distinct()
        section_results = SectionModel.objects.filter(
            chapter__law=law
        ).filter(
            Q(section_number__icontains=search_query)
            | Q(title__icontains=search_query)
            | Q(offense__icontains=search_query)
            | Q(penalty__icontains=search_query)
        ).select_related('chapter').order_by('chapter__chapter_number', 'section_number')

    if request.GET.get('ajax') == '1':
        return JsonResponse({
            'query': search_query,
            'chapters': [
                {
                    'id': chapter.id,
                    'chapter_number': chapter.chapter_number,
                    'title': chapter.title,
                }
                for chapter in chapters
            ],
            'sections': [
                {
                    'id': section.id,
                    'section_number': section.section_number,
                    'title': section.title or 'Untitled section',
                    'chapter_number': section.chapter.chapter_number,
                    'chapter_title': section.chapter.title,
                }
                for section in section_results
            ],
        })

    paginator = Paginator(chapters, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'law': law,
        'chapters': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'section_results': section_results,
    }
    return render(request, "website/chapter.html", context)


def section(request, chapter_id):
    chapter = get_object_or_404(ChapterModel, id=chapter_id)
    redirect_to_login = require_law_access(request, chapter.law)
    if redirect_to_login:
        return redirect_to_login

    save_user_history(request, law=chapter.law, chapter=chapter)

    search_query = request.GET.get('q', '').strip()
    sections = chapter.sections.all()
    if search_query:
        sections = sections.filter(
            Q(section_number__icontains=search_query)
            | Q(title__icontains=search_query)
            | Q(offense__icontains=search_query)
            | Q(penalty__icontains=search_query)
            | Q(note__icontains=search_query)
            | Q(case_law__icontains=search_query)
            | Q(directive__icontains=search_query)
        ).distinct()
    
    user_bookmarks = set()
    if request.user.is_authenticated:
        user_bookmarks = set(BookmarkModel.objects.filter(
            user=request.user, 
            section__chapter=chapter
        ).values_list('section_id', flat=True))
    
    context = {
        'chapter': chapter,
        'sections': sections,
        'search_query': search_query,
        'user_bookmarks': user_bookmarks
    }
    return render(request, "website/section.html", context)


def section_detail(request, section_id):
    section = get_object_or_404(SectionModel, id=section_id)
    redirect_to_login = require_law_access(request, section.chapter.law)
    if redirect_to_login:
        return redirect_to_login

    save_user_history(request, law=section.chapter.law, chapter=section.chapter, section=section)

    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = BookmarkModel.objects.filter(
            user=request.user, 
            section=section
        ).exists()

    context = {
        'section': section,
        'is_bookmarked': is_bookmarked
    }
    return render(request, "website/section_detail.html", context)

@login_required(login_url="/login/")
def profile(request):
    return render(request, "website/profile.html")
    
def privacy_policy(request):
    return render(request, "website/privacy_policy.html")  


def _plain_text(value):
    """Rich-text HTML ကို tag မပါတဲ့ စာသားသက်သက် ပြောင်းပေးတယ်"""
    if not value:
        return ''
    text = re.sub(r'<[^>]*>', ' ', value)
    text = html_lib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def _highlight(text, query):
    """စာသားကို escape လုပ်ပြီး ရှာထားတဲ့ keyword ကို <mark> နဲ့ ဝိုင်းပေးတယ်"""
    if not text:
        return ''
    escaped = str(escape(text))
    if not query:
        return mark_safe(escaped)
    pattern = re.compile(re.escape(str(escape(query))), re.IGNORECASE)
    return mark_safe(
        pattern.sub(lambda m: '<mark class="search-hit">%s</mark>' % m.group(0), escaped)
    )


def _snippet(text, query, before=40, length=150):
    """keyword ပါတဲ့နေရာ ပတ်ဝန်းကျင်စာသားကို ဖြတ်ယူတယ်"""
    if not text:
        return ''
    match = re.search(re.escape(query), text, re.IGNORECASE) if query else None
    start = max(0, match.start() - before) if match else 0
    end = min(len(text), start + length)
    snippet = text[start:end]
    if start > 0:
        snippet = '…' + snippet
    if end < len(text):
        snippet += '…'
    return snippet


def _match_rank(q_low, fields, number_field_index=None):
    """
    fields = ဦးစားပေးအလိုက် စာသားစာရင်း။
    ရလဒ်: ဦးစားပေးအမှတ် (နည်းလေ ကောင်းလေ)၊ တကယ် မတွေ့ရင် None
    exact = i*3, startswith = i*3+1, contains = i*3+2
    """
    for i, field in enumerate(fields):
        text = (field or '').lower()
        if not text:
            continue
        candidates = [text]
        if i == number_field_index and text.split():
            candidates.append(text.split()[-1])  # "ပုဒ်မ ၆၀" -> "၆၀"
        if any(c == q_low for c in candidates):
            return i * 3
        if any(c.startswith(q_low) for c in candidates):
            return i * 3 + 1
        if q_low in text:
            return i * 3 + 2
    return None


def _natural_key(value):
    token = (value or '').split()[-1] if (value or '').split() else ''
    return (len(token), token)


def global_search(request):
    """Global Search အတွက် View"""
    query = request.GET.get('q', '').strip()

    if query and request.user.is_authenticated and (
        request.GET.get('ajax') != '1' or request.GET.get('save_history') == '1'
    ):
        search, created = SearchHistoryModel.objects.get_or_create(
            user=request.user,
            query=query,
        )
        if not created:
            search.updated_at = now()
            search.save(update_fields=('updated_at',))

    law_results = []
    chapter_results = []
    section_results = []

    if query:
        q_low = query.lower()
        full_access = request.user.is_authenticated and request.user.is_active

        laws_qs = LawModel.objects.all()
        chapters_qs = ChapterModel.objects.all()
        sections_qs = SectionModel.objects.all()
        if not full_access:
            # Inactive/non-authenticated users can only see free laws
            laws_qs = laws_qs.filter(is_free=True)
            chapters_qs = chapters_qs.filter(law__is_free=True)
            sections_qs = sections_qs.filter(chapter__law__is_free=True)

        # DB မှာ အကြမ်းစစ်ပြီး Python မှာ tag မပါတဲ့ စာသားနဲ့ ပြန်စစ်တယ်
        # (Chapter/Law title ပါတာနဲ့ section အားလုံးပါမလာအောင် ဖယ်ထားတယ်)
        laws_qs = laws_qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()
        chapters_qs = chapters_qs.filter(
            Q(chapter_number__icontains=query) | Q(title__icontains=query)
        ).distinct().select_related('law')
        sections_qs = sections_qs.filter(
            Q(section_number__icontains=query) | Q(title__icontains=query)
            | Q(offense__icontains=query) | Q(penalty__icontains=query)
        ).distinct().select_related('chapter__law')

        ranked = []
        for law in laws_qs:
            desc = _plain_text(law.description)
            rank = _match_rank(q_low, [law.title, desc])
            if rank is None:
                continue
            law.title_html = _highlight(law.title, query)
            law.snippet_html = _highlight(_snippet(desc, query), query)
            ranked.append((rank, law.title, law))
        law_results = [x[2] for x in sorted(ranked, key=lambda x: (x[0], x[1]))]

        ranked = []
        for chapter in chapters_qs:
            rank = _match_rank(q_low, [chapter.chapter_number, chapter.title], number_field_index=0)
            if rank is None:
                continue
            chapter.number_html = _highlight(chapter.chapter_number, query)
            chapter.title_html = _highlight(chapter.title, query)
            ranked.append((rank, _natural_key(chapter.chapter_number), chapter))
        chapter_results = [x[2] for x in sorted(ranked, key=lambda x: (x[0], x[1]))]

        ranked = []
        for section in sections_qs:
            offense = _plain_text(section.offense)
            penalty = _plain_text(section.penalty)
            rank = _match_rank(
                q_low,
                [section.section_number, section.title, offense, penalty],
                number_field_index=0,
            )
            if rank is None:
                continue
            # snippet: စာသားထဲမှာ ပါတဲ့နေရာကို ပြ၊ မဟုတ်ရင် offense အစကို ပြ
            if q_low in offense.lower():
                snippet_source = offense
            elif q_low in penalty.lower():
                snippet_source = penalty
            else:
                snippet_source = offense
            section.number_html = _highlight(section.section_number, query)
            section.title_html = _highlight(section.title or '', query)
            section.snippet_html = _highlight(_snippet(snippet_source, query), query)
            ranked.append((rank, _natural_key(section.section_number), section))
        section_results = [x[2] for x in sorted(ranked, key=lambda x: (x[0], x[1]))]

    law_count = len(law_results)
    chapter_count = len(chapter_results)
    section_count = len(section_results)
    total_results_count = law_count + chapter_count + section_count

    if request.GET.get('ajax') == '1':
        return JsonResponse({
            'query': query,
            'total_results_count': total_results_count,
            'laws': [
                {
                    'id': law.id,
                    'title': law.title,
                    'title_html': str(law.title_html),
                    'description': law.description or '',
                    'snippet_html': str(law.snippet_html),
                }
                for law in law_results[:20]
            ],
            'chapters': [
                {
                    'id': chapter.id,
                    'chapter_number': chapter.chapter_number,
                    'number_html': str(chapter.number_html),
                    'title': chapter.title,
                    'title_html': str(chapter.title_html),
                    'law_title': chapter.law.title,
                }
                for chapter in chapter_results[:20]
            ],
            'sections': [
                {
                    'id': section.id,
                    'section_number': section.section_number,
                    'number_html': str(section.number_html),
                    'title': section.title or '',
                    'title_html': str(section.title_html),
                    'snippet_html': str(section.snippet_html),
                    'chapter_title': section.chapter.title,
                    'law_title': section.chapter.law.title,
                }
                for section in section_results[:30]
            ]
        })

    context = {
        'query': query,
        'law_results': law_results,
        'chapter_results': chapter_results,
        'section_results': section_results,
        'total_results_count': total_results_count
    }
    return render(request, "website/search_result.html", context)


@login_required(login_url="/login/")
def bookmarks(request):
    """View to list all bookmarked sections for the logged-in user."""
    user_bookmarks = BookmarkModel.objects.filter(
        user=request.user
    ).select_related('section__chapter__law').order_by('-created_at')
    
    context = {
        'bookmarks': user_bookmarks
    }
    return render(request, "website/bookmarks.html", context)


@login_required(login_url="/login/")
def history(request):
    """View to list the user's saved reading history entries.

    Each entry is one unique law, chapter, or section record. This is displayed in a
    bookmark-style list so the user can revisit recently opened content without duplicates.
    """
    history_entries = UserHistoryModel.objects.filter(
        user=request.user
    ).select_related(
        'law',
        'chapter__law',
        'section__chapter__law'
    ).order_by('-updated_at')

    context = {
        'history_entries': history_entries,
    }
    return render(request, "website/history.html", context)


def downloads(request):
    """View to display downloaded sections for offline reading."""
    return render(request, "website/downloads.html")


@require_POST
def toggle_bookmark(request):
    """AJAX endpoint to add/remove a section bookmark."""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False, 
            'error': 'login_required', 
            'message': 'Please login to bookmark sections.'
        })
        
    try:
        data = json.loads(request.body)
        section_id = data.get('section_id')
    except Exception:
        section_id = request.POST.get('section_id')
        
    if not section_id:
        return JsonResponse({'success': False, 'message': 'Section ID is required.'}, status=400)
        
    section = get_object_or_404(SectionModel, id=section_id)
    
    bookmark, created = BookmarkModel.objects.get_or_create(
        user=request.user,
        section=section
    )
    
    if not created:
        # Already bookmarked, so remove it
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
        
    return JsonResponse({
        'success': True,
        'bookmarked': bookmarked
    })

def page404(request, exception=None):
    return render(request, "website/page404.html", status=404)


def get_myanmar_font():
    """Helper to locate a Myanmar font on Windows and register it for ReportLab."""
    font_paths = [
        "C:\\Windows\\Fonts\\mmrtext.ttf",
        "C:\\Windows\\Fonts\\pyidaungsu.ttf",
        "C:\\Windows\\Fonts\\padauk.ttf",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont("MyanmarFont", font_path))
                return "MyanmarFont"
            except Exception:
                pass
    return "Helvetica"


def download_section_pdf(request, section_id):
    """Generates and downloads a beautifully formatted PDF for the specified section."""
    section = get_object_or_404(SectionModel, id=section_id)

    redirect_to_login = require_law_access(request, section.chapter.law)
    if redirect_to_login:
        return redirect_to_login

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=colors.A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    font_name = get_myanmar_font()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="LawTitle",
        fontName=font_name,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#0d1b3e"),
        alignment=1,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        name="LawSubtitle",
        fontName=font_name,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#666666"),
        alignment=1,
        spaceAfter=12,
    )

    section_num_style = ParagraphStyle(
        name="SecNum",
        fontName=font_name,
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#0d1b3e"),
        bold=True,
        spaceAfter=4,
    )

    section_title_style = ParagraphStyle(
        name="SecTitle",
        fontName=font_name,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#333333"),
        spaceAfter=15,
    )

    label_style = ParagraphStyle(
        name="LabelStyle",
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0d1b3e"),
        bold=True,
        spaceAfter=6,
    )

    penalty_label_style = ParagraphStyle(
        name="PenaltyLabel",
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#d4a017"),
        bold=True,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        fontName=font_name,
        fontSize=11,
        leading=18,
        textColor=colors.HexColor("#444444"),
        spaceAfter=15,
    )

    elements = []
    elements.append(Paragraph(section.chapter.law.title, title_style))
    elements.append(Paragraph(f"{section.chapter.chapter_number} — {section.chapter.title}", subtitle_style))

    divider = Table([['']], colWidths=[523], rowHeights=[1])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(divider)
    elements.append(Spacer(1, 15))

    sec_num_text = f"Section {section.section_number}"
    elements.append(Paragraph(sec_num_text, section_num_style))
    if section.title:
        elements.append(Paragraph(section.title, section_title_style))

    elements.append(Paragraph("ပြစ်မှု", label_style))
    elements.append(Paragraph(section.offense, body_style))

    elements.append(Paragraph("ပြစ်ဒဏ်", penalty_label_style))
    penalty_data = [[Paragraph(section.penalty, body_style)]]
    penalty_table = Table(penalty_data, colWidths=[510])
    penalty_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbee")),
        ('LINELEFT', (0, 0), (0, -1), 4, colors.HexColor("#d4a017")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(penalty_table)
    elements.append(Spacer(1, 15))

    if section.note:
        elements.append(Paragraph("မှတ်ချက်", label_style))
        elements.append(Paragraph(section.note, body_style))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    filename = f"Section_{section.section_number.replace(' ', '_')}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def download_section_txt(request, section_id):
    """Generates and downloads a plain text file for the specified section."""
    section = get_object_or_404(SectionModel, id=section_id)

    redirect_to_login = require_law_access(request, section.chapter.law)
    if redirect_to_login:
        return redirect_to_login

    content = f"ဥပဒေအမည် - {section.chapter.law.title}\n"
    content += f"အခန်း - {section.chapter.chapter_number} {section.chapter.title}\n"
    content += f"--------------------------------------------------\n"
    content += f"ပုဒ်မ - {section.section_number}"
    if section.title:
        content += f" ({section.title})"
    content += "\n\n"
    content += f"[ပြစ်မှု]\n{section.offense}\n\n"
    content += f"[ပြစ်ဒဏ်]\n{section.penalty}\n"
    if section.note:
        content += f"\n[မှတ်ချက်]\n{section.note}\n"

    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    filename = f"Section_{section.section_number.replace(' ', '_')}.txt"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response