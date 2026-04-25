from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from .models import JobDescription, CV, MatchReport
from .services import ResumeAnalysisService
from .forms import JDForm, CVForm
from services.access import FeatureAccessMixin
from services.ai_router import record_token_usage

class ResumeAnalysisView(FeatureAccessMixin, View):
    feature_key = "resume_analysis"
    template_name="services/resume_analysis/analysis.html"

    def get(self, request):
        jds=JobDescription.objects.filter(user=request.user)
        cvs=CV.objects.filter(user=request.user)
        return render(request,self.template_name,{"jds":jds,"cvs":cvs,"jd_form":JDForm(),"cv_form":CVForm()})

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
        try:
            results=ResumeAnalysisService().compare(jd_id,cv_ids,user=request.user)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        record_token_usage(request.user, "resume_analysis", jd_id, f"JD {jd_id} CVs {','.join(cv_ids)}", str(results))
        return JsonResponse({"results":results})
