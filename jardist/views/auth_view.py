from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from jardist.forms.login_form import LoginForm
from jardist.decorators import login_and_group_required

def LoginPage(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Berhasil Masuk!')
                return redirect('list_pk')
            else:
                messages.error(request, 'Username atau Password salah')
        else:
            messages.error(request, 'Username atau Password salah')

    return render(request, 'pages/login_page.html', {'form': form})

@login_and_group_required()
def Logout(request):
    request.session.flush()
    logout(request)
    messages.success(request, 'Berhasil Keluar!')
    return redirect('login')