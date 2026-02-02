from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def ws_test(request):
    return render(request, template_name="chat/ws_test.html")
