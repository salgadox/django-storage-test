from django.shortcuts import render


def upload_form(request):
    return render(request, "videos/upload_form.html")
