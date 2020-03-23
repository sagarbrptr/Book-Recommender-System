
from django.conf.urls import url
from django.contrib import admin
from student import views as studentView
from librarian import views as librarianView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', studentView.home, name = "studentHome"),
    url(r'^recommendLibrary$', studentView.recommendLibrary, name = "recommendLibrary"),
    url(r'^librarian$', librarianView.librarianHome, name = "librarianHome")
]
