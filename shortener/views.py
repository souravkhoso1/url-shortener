from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ShortenedURL
from .forms import URLForm


def home(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['url']

            # Check if URL already exists
            existing = ShortenedURL.objects.filter(original_url=original_url).first()
            if existing:
                shortened = existing
            else:
                short_code = ShortenedURL.generate_short_code()
                shortened = ShortenedURL.objects.create(
                    original_url=original_url,
                    short_code=short_code
                )

            short_url = request.build_absolute_uri(f'/{shortened.short_code}')
            return render(request, 'shortener/home.html', {
                'form': URLForm(),
                'short_url': short_url,
                'shortened': shortened
            })
    else:
        form = URLForm()

    recent_urls = ShortenedURL.objects.all()[:10]
    return render(request, 'shortener/home.html', {
        'form': form,
        'recent_urls': recent_urls
    })


def redirect_url(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.original_url)


def stats(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    return render(request, 'shortener/stats.html', {'url_obj': url_obj})