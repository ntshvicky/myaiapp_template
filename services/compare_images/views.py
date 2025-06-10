from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import ImageCompareService
from .models import CompareSession, ComparisonResult
from .forms import CompareForm

class CompareView(LoginRequiredMixin, View):
    template_name="services/compare_images/compare.html"

    def get(self,request):
        form=CompareForm()
        return render(request,self.template_name,{"form":form})

    def post(self,request):
        form=CompareForm(request.POST,request.FILES)
        if not form.is_valid():
            return render(request,self.template_name,{"form":form})
        session=CompareSession.objects.create(user=request.user)
        img1=form.cleaned_data["image1"]
        img2=form.cleaned_data["image2"]
        res=ImageCompareService().compare(img1,img2)
        comp=ComparisonResult.objects.create(
            session=session,
            image1=img1, image2=img2,
            score=res["score"], diff_url=res["diff_url"]
        )
        return render(request,self.template_name,{"form":form,"result":comp})
