from django.shortcuts import render


def interface(request):
    return render(request, 'avatar/index.html')

