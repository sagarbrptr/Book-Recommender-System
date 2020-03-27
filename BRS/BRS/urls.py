
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from student import views as studentView
from librarian import views as librarianView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', studentView.home, name = "studentHome"),
    url(r'^recommendLibrary$', studentView.recommendLibrary, name = "recommendLibrary"),
    url(r'^studentRecommendation$', studentView.studentRecommendation, name = "studentRecommendation"),

    
    url(r'^librarianHome$', librarianView.librarianHome, name = "librarianHome"),
    url(r'^librarianRecommendation$', librarianView.librarianRecommendation, name = "librarianRecommendation"),
    url(r'^librarianStatistics$', librarianView.librarianStatistics, name = "librarianStatistics"),
    ]

urlpatterns += staticfiles_urlpatterns()