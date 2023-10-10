from django.urls import path 
from . import views

app_name = "home"

urlpatterns = [
    path("", views.LandingView.as_view(), name="landing_page"),
    path("contact-us/", views.contact_us, name="contact-us"),
]