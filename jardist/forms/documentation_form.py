from django import forms
from django.forms import inlineformset_factory
from jardist.models.task_models import Task, TaskDocumentation, TaskDocumentationPhoto
from jardist.models.contract_models import PK

class TaskDocumentationForm(forms.Form):
    pk_instance = forms.ModelChoiceField(queryset=PK.objects.all(), label='No. PK', widget=forms.Select(attrs={'class': 'form-select', 'id': 'pk_instance'}))
    task_instance = forms.ModelChoiceField(queryset=Task.objects.none(), label='Nama Pekerjaan', widget=forms.Select(attrs={'class': 'form-select', 'id': 'task_instance'}))
    location = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link Titik GMaps', 'id': 'location'}), label='Lokasi Pengerjaan')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pk_instance'].empty_label = 'Pilih No. PK'
        self.fields['task_instance'].empty_label = 'Pilih Nama Pekerjaan'
        self.fields['pk_instance'].queryset = PK.objects.all()

        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'pk_instance' in initial and initial['pk_instance'] is not None:
                self.fields['task_instance'].queryset = Task.objects.filter(pk_instance=initial['pk_instance'])
            else:
                self.fields['task_instance'].queryset = Task.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        pk_instance = cleaned_data.get('pk_instance')
        task_instance = cleaned_data.get('task_instance')

        if task_instance and task_instance.pk_instance != pk_instance:
            self.add_error('task_instance', 'The selected task does not belong to the chosen PK.')

    def save(self):
        task_instance = self.cleaned_data['task_instance']
        location = self.cleaned_data['location']

        task_documentation, created = TaskDocumentation.objects.get_or_create(
            task=task_instance,
            defaults={'location': location}
        )

        if not created:
            task_documentation.location = location
            task_documentation.save()

        return task_documentation

class TaskDocumentationPhotoForm(forms.ModelForm):
    class Meta:
        model = TaskDocumentationPhoto
        fields = ['photo', 'description']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg, .jpeg, .png', 'required': True}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deskripsi Foto', 'required': True}),
        }
        labels = {
            'photo': 'Foto',
            'description': 'Keterangan',
        }

TaskDocumentationPhotoFormSet = inlineformset_factory(
    parent_model=TaskDocumentation,
    model=TaskDocumentationPhoto,
    form=TaskDocumentationPhotoForm,
    extra=1,
    can_delete=True,
)