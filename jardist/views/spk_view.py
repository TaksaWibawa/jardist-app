from django.shortcuts import render, redirect
from jardist.forms.spk_form import SPKForm
from django.contrib import messages

def CreateSPKPage(request):
    form = SPKForm()

    if request.method == 'POST':
        form = SPKForm(request.POST)
        if form.is_valid():
            spk = form.save(commit=False)
            if hasattr(request.user, 'userprofile'):
                spk.department = request.user.userprofile.department
            spk.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('home')
        else:
            messages.error(request, 'Data gagal disimpan')
        
    context = {'form': form}

    return render(request, 'pages/create_spk_page.html', context)