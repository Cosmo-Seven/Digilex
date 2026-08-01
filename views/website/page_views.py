from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from core.models import LawModel, ChapterModel, SectionModel, BookmarkModel
import json
import os
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def require_law_access(request, law):
    if law.is_free or request.user.is_authenticated:
        return None
    return redirect("login")


def index(request):
    laws = LawModel.objects.all()
    context = {
        'laws': laws
    }
    return render(request, "website/index.html", context)


def chapter(request, law_id):
    law = get_object_or_404(LawModel, id=law_id)
    redirect_to_login = require_law_access(request, law)
    if redirect_to_login:
        return redirect_to_login

    chapters = law.chapters.all().order_by('chapter_number')
    paginator = Paginator(chapters, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'law': law,
        'chapters': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, "website/chapter.html", context)


def section(request, chapter_id):
    chapter = get_object_or_404(ChapterModel, id=chapter_id)
    redirect_to_login = require_law_access(request, chapter.law)
    if redirect_to_login:
        return redirect_to_login

    sections = chapter.sections.all()
    
    user_bookmarks = set()
    if request.user.is_authenticated:
        user_bookmarks = set(BookmarkModel.objects.filter(
            user=request.user, 
            section__chapter=chapter
        ).values_list('section_id', flat=True))
    
    context = {
        'chapter': chapter,
        'sections': sections,
        'user_bookmarks': user_bookmarks
    }
    return render(request, "website/section.html", context)


def section_detail(request, section_id):
    section = get_object_or_404(SectionModel, id=section_id)
    redirect_to_login = require_law_access(request, section.chapter.law)
    if redirect_to_login:
        return redirect_to_login

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

def profile(request):
    return render(request, "website/profile.html")
    
def privacy_policy(request):
    return render(request, "website/privacy_policy.html")  


def global_search(request):
    """Global Search အတွက် View"""
    query = request.GET.get('q', '').strip()
    
    law_results = []
    chapter_results = []
    section_results = []

    if query:
        law_results = LawModel.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()

        chapter_results = ChapterModel.objects.filter(
            Q(chapter_number__icontains=query) | Q(title__icontains=query) | Q(law__title__icontains=query)
        ).distinct().select_related('law')

        section_results = SectionModel.objects.filter(
            Q(section_number__icontains=query) | Q(offense__icontains=query) | Q(penalty__icontains=query) |
            Q(chapter__title__icontains=query) | Q(chapter__law__title__icontains=query)
        ).distinct().select_related('chapter__law')

    law_count = law_results.count() if query else 0
    chapter_count = chapter_results.count() if query else 0
    section_count = section_results.count() if query else 0
    total_results_count = law_count + chapter_count + section_count

    if request.GET.get('ajax') == '1':
        return JsonResponse({
            'query': query,
            'total_results_count': total_results_count,
            'laws': [
                {
                    'id': law.id,
                    'title': law.title,
                    'description': law.description or ''
                }
                for law in law_results
            ],
            'chapters': [
                {
                    'id': chapter.id,
                    'chapter_number': chapter.chapter_number,
                    'title': chapter.title,
                    'law_title': chapter.law.title
                }
                for chapter in chapter_results
            ],
            'sections': [
                {
                    'id': section.id,
                    'section_number': section.section_number,
                    'title': section.title or '',
                    'offense': section.offense,
                    'chapter_title': section.chapter.title,
                    'law_title': section.chapter.law.title
                }
                for section in section_results
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

def page404(request):
    return render(request, "website/page404.html")


# def get_myanmar_font():
#     """Helper to locate a Myanmar font on Windows and register it for ReportLab."""
#     font_paths = [
#         "C:\\Windows\\Fonts\\mmrtext.ttf",      # Myanmar Text (standard Windows font)
#         "C:\\Windows\\Fonts\\pyidaungsu.ttf",    # Pyidaungsu
#         "C:\\Windows\\Fonts\\padauk.ttf",        # Padauk
#     ]
#     for font_path in font_paths:
#         if os.path.exists(font_path):
#             try:
#                 pdfmetrics.registerFont(TTFont("MyanmarFont", font_path))
#                 return "MyanmarFont"
#             except Exception:
#                 pass
#     return "Helvetica"


# def download_section_pdf(request, section_id):
#     """Generates and downloads a beautifully formatted PDF for the specified section."""
#     section = get_object_or_404(SectionModel, id=section_id)
    
#     # Require access check
#     redirect_to_login = require_law_access(request, section.chapter.law)
#     if redirect_to_login:
#         return redirect_to_login

#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer,
#         pagesize=colors.A4,
#         rightMargin=36,
#         leftMargin=36,
#         topMargin=36,
#         bottomMargin=36,
#     )
    
#     font_name = get_myanmar_font()
#     styles = getSampleStyleSheet()
    
#     # Custom Paragraph Styles
#     title_style = ParagraphStyle(
#         name="LawTitle",
#         fontName=font_name,
#         fontSize=18,
#         leading=24,
#         textColor=colors.HexColor("#0d1b3e"),
#         alignment=0, # Left-aligned
#         spaceAfter=4,
#     )
    
#     subtitle_style = ParagraphStyle(
#         name="LawSubtitle",
#         fontName=font_name,
#         fontSize=11,
#         leading=16,
#         textColor=colors.HexColor("#666666"),
#         alignment=0,
#         spaceAfter=12,
#     )
    
#     section_num_style = ParagraphStyle(
#         name="SecNum",
#         fontName=font_name,
#         fontSize=15,
#         leading=20,
#         textColor=colors.HexColor("#0d1b3e"),
#         bold=True,
#         spaceAfter=4,
#     )
    
#     section_title_style = ParagraphStyle(
#         name="SecTitle",
#         fontName=font_name,
#         fontSize=14,
#         leading=18,
#         textColor=colors.HexColor("#333333"),
#         spaceAfter=15,
#     )
    
#     label_style = ParagraphStyle(
#         name="LabelStyle",
#         fontName=font_name,
#         fontSize=10,
#         leading=14,
#         textColor=colors.HexColor("#0d1b3e"),
#         bold=True,
#         spaceAfter=6,
#     )
    
#     penalty_label_style = ParagraphStyle(
#         name="PenaltyLabel",
#         fontName=font_name,
#         fontSize=10,
#         leading=14,
#         textColor=colors.HexColor("#d4a017"),
#         bold=True,
#         spaceAfter=6,
#     )
    
#     body_style = ParagraphStyle(
#         name="BodyStyle",
#         fontName=font_name,
#         fontSize=11,
#         leading=18,
#         textColor=colors.HexColor("#444444"),
#         spaceAfter=15,
#     )
    
#     elements = []
    
#     # 1. Header Information
#     elements.append(Paragraph(section.chapter.law.title, title_style))
#     elements.append(Paragraph(f"{section.chapter.chapter_number} — {section.chapter.title}", subtitle_style))
    
#     # 2. Divider Line
#     divider = Table([['']], colWidths=[523], rowHeights=[1])
#     divider.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
#         ('TOPPADDING', (0, 0), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
#     ]))
#     elements.append(divider)
#     elements.append(Spacer(1, 15))
    
#     # 3. Section Number and Title
#     sec_num_text = f"Section {section.section_number}"
#     elements.append(Paragraph(sec_num_text, section_num_style))
#     if section.title:
#         elements.append(Paragraph(section.title, section_title_style))
    
#     # 4. Offense Section
#     elements.append(Paragraph("ပြစ်မှု", label_style))
#     elements.append(Paragraph(section.offense, body_style))
    
#     # 5. Penalty Section (Box styling)
#     elements.append(Paragraph("ပြစ်ဒဏ်", penalty_label_style))
#     penalty_data = [[Paragraph(section.penalty, body_style)]]
#     penalty_table = Table(penalty_data, colWidths=[510])
#     penalty_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbee")),
#         ('LINELEFT', (0, 0), (0, -1), 4, colors.HexColor("#d4a017")),
#         ('LEFTPADDING', (0, 0), (-1, -1), 12),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 12),
#         ('TOPPADDING', (0, 0), (-1, -1), 10),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
#     ]))
#     elements.append(penalty_table)
#     elements.append(Spacer(1, 15))
    
#     # 6. Note Section (optional)
#     if section.note:
#         elements.append(Paragraph("မှတ်ချက်", label_style))
#         elements.append(Paragraph(section.note, body_style))
        
#     doc.build(elements)
#     buffer.seek(0)
    
#     response = HttpResponse(buffer, content_type="application/pdf")
#     filename = f"Section_{section.section_number.replace(' ', '_')}.pdf"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#     return response


# def download_section_txt(request, section_id):
#     """Generates and downloads a plain text file for the specified section."""
#     section = get_object_or_404(SectionModel, id=section_id)
    
#     # Require access check
#     redirect_to_login = require_law_access(request, section.chapter.law)
#     if redirect_to_login:
#         return redirect_to_login
        
#     content = f"ဥပဒေအမည် - {section.chapter.law.title}\n"
#     content += f"အခန်း - {section.chapter.chapter_number} {section.chapter.title}\n"
#     content += f"--------------------------------------------------\n"
#     content += f"ပုဒ်မ - {section.section_number}"
#     if section.title:
#         content += f" ({section.title})"
#     content += "\n\n"
#     content += f"[ပြစ်မှု]\n{section.offense}\n\n"
#     content += f"[ပြစ်ဒဏ်]\n{section.penalty}\n"
#     if section.note:
#         content += f"\n[မှတ်ချက်]\n{section.note}\n"
        
#     response = HttpResponse(content, content_type="text/plain; charset=utf-8")
#     filename = f"Section_{section.section_number.replace(' ', '_')}.txt"
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#     return response