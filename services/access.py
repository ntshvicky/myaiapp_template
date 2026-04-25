from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class FeatureAccessMixin(LoginRequiredMixin):
    feature_key = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.feature_key and not request.user.can_access_feature(self.feature_key):
            messages.error(request, "Upgrade your plan to use this AI tool.")
            return redirect("pricing")
        return super().dispatch(request, *args, **kwargs)
