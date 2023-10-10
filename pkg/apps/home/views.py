from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from .tasks import contact_us_email

# Create your views here.
class LandingView(TemplateView):
    template_name = "home/landing_page.html"


@require_POST
def contact_us(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    message = request.POST.get("message")
    contact_us_email.delay(name, email, message)
    return render(request, "home/partials/_contact_success.html")