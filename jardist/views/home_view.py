from django.shortcuts import render

def HomePage(request):
    return render(request, 'pages/home_page.html')