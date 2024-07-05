from django import forms
from jardist.models.contract_models import SPK, PK
from jardist.models.task_models import Task

class BASTForm(forms.ModelForm):
    spk_instance = forms.ModelChoiceField(queryset=SPK.objects.all(), empty_label='Pilih No. SPK', widget=forms.Select(attrs={'class': 'form-control', 'id': 'spk_instance'}), label='No. SPK')

    class Meta:
        model = PK
        fields = ['pk_number', 'bast_date']
        widgets = {
            'pk_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'pk_number'}),
            'bast_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'id': 'bast_date', 'type': 'date', 'required': True}),
        }
        labels = {
            'pk_number': 'No. PK',
            'bast_date': 'Pilih Tanggal BAST I',
            'end_date': 'Tanggal Berakhir PK',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['spk_instance'].initial = self.instance.spk

class RealizationTaskForm(forms.ModelForm):
    class Meta:
        TASK_STATUS_CHOICES = [
            ('', 'Pilih Status Pekerjaan'),
            ('On Progress', 'On Progress'),
            ('Done', 'Done'),
        ]
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(choices=TASK_STATUS_CHOICES, attrs={'class': 'form-control w-100', 'id': 'status'}),
        }
        labels = {
            'status': 'Status Pekerjaan',
        }

UpdateTaskStatusFormset = forms.modelformset_factory(Task, form=RealizationTaskForm, extra=0)