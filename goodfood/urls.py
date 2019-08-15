from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from listings import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^zomato-collect', views.ZomatoCollect, name='zomato-collect'),
    url(r'^google-scrap', views.GoogleEstablishmentsCollection, name='google-places-scrap'),
    url(r'^google-place-details', views.GooglePlaceDetailsCollection, name='google-place-details'),
    url(r'^google-photo-collect', views.GooglePlacePhotoCollection, name='google-photo-collection'),
    url(r'^google-url-shorten', views.UrlShortener, name='google-url-shortener'),
    url(r'^map-quest', views.MapQuestAPI, name='map-quest'),
    url(r'^google-collection', views.GoogleCollection, name='google-collection'),
    url(r'^landing', views.landing, name='landing'),
    url(r'^test', views.test, name='test'),
    url(r'^admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

