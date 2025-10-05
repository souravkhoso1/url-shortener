# shortener/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import ShortenedURL
from .forms import URLForm, UserRegisterForm, UserLoginForm


def home(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['url']

            # Check if URL already exists for this user
            if request.user.is_authenticated:
                existing = ShortenedURL.objects.filter(
                    original_url=original_url,
                    user=request.user
                ).first()
            else:
                existing = None

            if existing:
                shortened = existing
            else:
                short_code = ShortenedURL.generate_short_code()
                shortened = ShortenedURL.objects.create(
                    original_url=original_url,
                    short_code=short_code,
                    user=request.user if request.user.is_authenticated else None
                )

            short_url = request.build_absolute_uri(f'/{shortened.short_code}')

            # Get recent URLs based on authentication
            if request.user.is_authenticated:
                recent_urls = ShortenedURL.objects.filter(user=request.user)[:10]
            else:
                recent_urls = ShortenedURL.objects.filter(user__isnull=True)[:10]

            return render(request, 'shortener/home.html', {
                'form': URLForm(),
                'short_url': short_url,
                'shortened': shortened,
                'recent_urls': recent_urls
            })
    else:
        form = URLForm()

    # Show user's URLs if authenticated, otherwise show anonymous URLs
    if request.user.is_authenticated:
        recent_urls = ShortenedURL.objects.filter(user=request.user)[:10]
    else:
        recent_urls = ShortenedURL.objects.filter(user__isnull=True)[:10]

    return render(request, 'shortener/home.html', {
        'form': form,
        'recent_urls': recent_urls
    })


@login_required
def my_urls(request):
    urls = ShortenedURL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shortener/my_urls.html', {'urls': urls})


def redirect_url(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.original_url)


def stats(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)

    # Check if user owns this URL
    is_owner = request.user.is_authenticated and url_obj.user == request.user

    return render(request, 'shortener/stats.html', {
        'url_obj': url_obj,
        'is_owner': is_owner
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('shortener:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('shortener:login')
    else:
        form = UserRegisterForm()

    return render(request, 'shortener/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('shortener:home')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'shortener:home')
                return redirect(next_page)
    else:
        form = UserLoginForm()

    return render(request, 'shortener/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('shortener:home')