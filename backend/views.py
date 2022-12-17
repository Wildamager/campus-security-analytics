from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import permission_required, login_required 

@login_required
def home(request):
    return render(request, 'index/index.html',)

