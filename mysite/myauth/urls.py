from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (MyLogoutView,
                    get_cookie_view,
                    set_cookie_view,
                    set_session_view,
                    get_session_view,
                    AboutMeView,
                    RegistrationView,
                    FooBarView,
                    UserListView,
                    AccountDetailsView,
                    AccountUpdateView,
                    HelloView)

# from .views import

app_name = "myauth"

urlpatterns = [
    path("login/",
         LoginView.as_view(
             template_name='myauth/login.html',
             redirect_authenticated_user=True,
         ),
         name="login"),
    path('hello/', HelloView.as_view(), name='hello'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about-me'),
    path('', UserListView.as_view(), name='users-list'),
    path('<int:pk>/', AccountDetailsView.as_view(), name='account_detail'),
    path('profile/<int:pk>/update', AccountUpdateView.as_view(), name='account_update'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),
    path('session/get/', get_session_view, name='session_get'),
    path('session/set/', set_session_view, name='session_set'),
    path('foo-bar/', FooBarView.as_view(), name="foo-bar")
]