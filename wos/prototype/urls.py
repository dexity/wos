
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns("wos.prototype.views",
    url(r"^$", "search"),
)