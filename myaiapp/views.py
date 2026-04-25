from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

class PricingView(View):
    template_name = 'pricing.html'

    def get(self, request):
        from django.shortcuts import render

        return render(request, self.template_name)

    def post(self, request):
        plan = request.POST.get("plan")
        valid_plans = {"free", "plus", "pro", "enterprise"}
        if plan not in valid_plans:
            messages.error(request, "Please choose a valid plan.")
            return redirect("pricing")
        if not request.user.is_authenticated:
            request.session["selected_plan"] = plan
            messages.info(request, "Create an account to activate your selected plan.")
            return redirect("accounts:register")
        request.user.subscription_plan = plan
        request.user.subscription_active = True
        request.user.save(update_fields=["subscription_plan", "subscription_active"])
        messages.success(request, f"{plan.title()} plan activated.")
        return redirect("dashboard")
