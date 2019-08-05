from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from listings import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^collect', views.collection, name='collection'),
    url(r'^test/(?P<username>\w{0,50})/$', views.test, name='test'),
    url(r'^admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)