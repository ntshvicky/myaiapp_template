from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import JobDescription, CV, MatchReport
from .services import ResumeAnalysisService
from .forms import JDForm, CVForm

class ResumeAnalysisView(LoginRequiredMixin, View):
    template_name="services/resume_analysis/analysis.html"

    def get(self, request):
        jds=JobDescription.objects.filter(user=request.user)
        cvs=CV.objects.filter(user=request.user)
        return render(request,self.template_name,{"jds":jds,"cvs":cvs})

    def post(self, request):
        if 'upload_jd' in request.POST:
            form=JDForm(request.POST,request.FILES)
            if form.is_valid():
                jd=form.save(commit=False); jd.user=request.user; jd.save()
            return redirect(request.path)
        if 'upload_cv' in request.POST:
            form=CVForm(request.POST,request.FILES)
            if form.is_valid():
                cv=form.save(commit=False); cv.user=request.user; cv.save()
            return redirect(request.path)
        # compare
        jd_id=request.POST.get("jd_id")
        cv_ids=request.POST.getlist("cv_ids")
        results=ResumeAnalysisService().compare(jd_id,cv_ids)
        return JsonResponse({"results":results})
