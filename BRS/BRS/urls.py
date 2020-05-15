
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from student import views as studentView
from librarian import views as librarianView
from login import views as loginView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', loginView.loginview, name = "login"),
    url(r'^login/$', loginView.loginview, name = "login"),
     url(r'^logout/$', loginView.logoutview, name = "logout"),

    # Student
    url(r'^studentHome$', studentView.studentHome, name = "studentHome"),
    url(r'^recommendLibrary$', studentView.recommendLibrary, name = "recommendLibrary"),
    url(r'^studentRecommendation$', studentView.studentRecommendation, name = "studentRecommendation"),
    url(r'^userProfile$', studentView.userProfile, name="userProfile"),
    url(r'^giveRating$', studentView.giveRating, name="giveRating"),

    # Librarian
    url(r'^librarianHome$', librarianView.librarianHome, name="librarianHome"),
    url(r'^librarianRecommendation$', librarianView.librarianRecommendation,
        name="librarianRecommendation"),
    url(r'^librarianStatistics$', librarianView.librarianStatistics,
        name="librarianStatistics"),
    url(r'^issueBook$', librarianView.issueBook, name="issueBook"),
]

urlpatterns += staticfiles_urlpatterns()