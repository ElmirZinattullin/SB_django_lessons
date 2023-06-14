from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.views.generic.edit import BaseUpdateView, ProcessFormView

from .models import Profile
from .forms import ProfileForm


# Create your views here.

class AboutMeView(View):
    template_name = 'myauth/about-me.html'
    model = Profile
    fields = 'bio', 'agreement_accepted', 'avatar'


    def get(self, request:HttpRequest) -> HttpResponse:

        user = request.user
        # profile = user.profile
        profile = Profile.objects.filter(user=user)
        if not profile:
            Profile.objects.create(user=user)
        form = ProfileForm(instance=request.user.profile)
        avatar = form.initial.get('avatar')
        context = {"form": form, 'avatar': avatar}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        # avatar = request.FILES.get('avatar')
        # request.user.profile.avatar = avatar
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class AccountDetailsView(DetailView):
    template_name = 'myauth/user_form.html'
    queryset = User.objects.select_related('profile').all()
    context_object_name = 'account'

    def get(self, request, *args, **kwargs):
        if kwargs['pk'] == request.user.pk:
            # print('eto ti sam')
            return HttpResponseRedirect(reverse_lazy('myauth:about-me'))
        return super().get(self, request, *args, **kwargs)


class AccountUpdateView(UserPassesTestMixin, UpdateView):
    queryset = Profile.objects.select_related('user')
    template_name = 'myauth/user_form_update.html'
    fields = 'avatar', 'bio',
    context_object_name = 'account'
    success_url = reverse_lazy('myauth:users-list')

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.filter(user_id=kwargs['pk'])
        if not profile:
            profile = Profile.objects.create(user_id=kwargs['pk'])
            profile.save()
        return super().get(self, request, *args, **kwargs)


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


class UserListView(ListView):
    template_name = "myauth/accounts_list.html"
    queryset = User.objects.select_related('profile').all()
    context_object_name = 'accounts'
    # queryset = Product.objects.filter(archived=False)

class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


def get_cookie_view(request:HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default_value')
    return HttpResponse(f"Cookie value: {value!r}")


def set_session_view(request:HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


def get_session_view(request:HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default')
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam" : "eggs"})