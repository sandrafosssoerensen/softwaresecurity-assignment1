from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [path("health", views.health)]
if settings.SERVICE == "A":
    urlpatterns += [path("auth/token", views.login), path("analyses", views.public_analyses),
                    path("analyses/<str:analysis_id>", views.public_analyses)]
elif settings.SERVICE == "B":
    urlpatterns += [path("internal/analyze", views.analyze)]
elif settings.SERVICE == "C":
    urlpatterns += [path("internal/analyses", views.stored_analyses),
                    path("internal/analyses/<str:analysis_id>", views.stored_analyses)]
else:
    raise ValueError("SERVICE must be A, B, or C")
