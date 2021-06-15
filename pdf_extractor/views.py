from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect


def index(request):
    # Render the HTML template index.html
    return HttpResponseRedirect(reverse('authentication:user_login'))
