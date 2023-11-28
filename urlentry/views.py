from django.http import HttpResponse
from .models import UrlEntry
from django.template import loader
from django.shortcuts import render


def index(request):
    url_entry_list = UrlEntry.objects.all()
    #template = loader.get_template()
    context = {
        "url_entry_list": url_entry_list
    }
    return render(request, "urlentry/index.html", context)
    #return HttpResponse(template.render(context, request))
    #return HttpResponse("Hello, world. You're at the urlentry index.")

def detail(request, short_code):
    original_url = UrlEntry.objects.get(short_url_code=short_code).original_url
    return HttpResponse(f"Short code: {short_code}, Main URL: {original_url}")

