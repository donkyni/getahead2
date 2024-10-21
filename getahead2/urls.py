from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from affiliation import views
#from affiliation.views import generate_lien

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.produitfrontend, name='produitfrontend'),
    path('affiliation/', include('affiliation.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    #path('<slug:unique_id>/lien-generer-pour-l-inscription-a-getahead-2.0/$', generate_lien, name="generate_lien"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

