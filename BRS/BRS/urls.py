
from django.conf.urls import url
from django.contrib import admin
from student import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name = "studentHome"),
    url(r'^recommendLibrary$', views.recommendLibrary, name = "recommendLibrary")
]

urlpatterns += staticfiles_urlpatterns()