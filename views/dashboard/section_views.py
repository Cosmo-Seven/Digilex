from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import ChapterModel, SectionModel
from utils.decorators import custom_login_required

@custom_login_required("dashboard_login")
def section_list(request, chapter_id):
    chapter = get_object_or_404(ChapterModel, id=chapter_id)
    sections = SectionModel.objects.filter(chapter=chapter).order_by('section_number')
    return render(request, "dashboard/section_list.html", {"chapter": chapter, "sections": sections})

@custom_login_required("dashboard_login")
def section_create(request, chapter_id):
    chapter = get_object_or_404(ChapterModel, id=chapter_id)
    if request.method == "POST":
        section_number = request.POST.get("section_number")
        title = request.POST.get("title")
        offense = request.POST.get("offense")
        penalty = request.POST.get("penalty")
        note = request.POST.get("note")
        SectionModel.objects.create(chapter=chapter, section_number=section_number, title=title, offense=offense, penalty=penalty, note=note)
        return redirect("section_list", chapter_id=chapter.id)
    return redirect("section_list", chapter_id=chapter.id)

@custom_login_required("dashboard_login")
def section_update(request, chapter_id, pk):
    chapter = get_object_or_404(ChapterModel, id=chapter_id)
    section = get_object_or_404(SectionModel, id=pk, chapter=chapter)
    if request.method == "POST":
        section.section_number = request.POST.get("section_number")
        section.title = request.POST.get("title")
        section.offense = request.POST.get("offense")
        section.penalty = request.POST.get("penalty")
        section.note = request.POST.get("note")
        section.save()
        return redirect("section_list", chapter_id=chapter.id)
    return redirect("section_list", chapter_id=chapter.id)

@custom_login_required("dashboard_login")
def section_delete(request, chapter_id, pk):
    section = get_object_or_404(SectionModel, id=pk, chapter_id=chapter_id)
    section.delete()
    return redirect("section_list", chapter_id=chapter_id)
