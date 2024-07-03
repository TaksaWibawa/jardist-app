from django import forms
from jardist.models.contract_models import SPK
from jardist.models.task_models import Task

TASK_STATUS_CHOICES = [
    ('', 'Pilih Status Pekerjaan'),
    ('On Progress', 'On Progress'),
    ('Done', 'Done'),
]

class RealizationTaskForm(forms.ModelForm):
    spk_instance = forms.ModelChoiceField(queryset=SPK.objects.all(), empty_label='Pilih No. SPK', widget=forms.Select(attrs={'class': 'form-select', 'id': 'spk_instance'}), label='No. SPK')
    end_date_pk = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'id': 'end_date_pk', 'type': 'date'}), label='Tanggal Berakhir PK')

    class Meta:
        model = Task
        fields = ['pk_instance', 'location', 'customer_name', 'task_type', 'status']
        widgets = {
            'pk_instance': forms.Select(attrs={'class': 'form-select', 'id': 'pk_instance', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'customer_name'}),
            'task_type': forms.Select(attrs={'class': 'form-select', 'id': 'task_type'}),
            'status': forms.Select(choices=TASK_STATUS_CHOICES, attrs={'class': 'form-select', 'id': 'status'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['spk_instance'].initial = self.instance.pk_instance.spk if self.instance.pk_instance else None
            self.fields['end_date_pk'].initial = self.instance.pk_instance.end_date if self.instance.pk_instance else None

    def save(self, commit=True):
        self.instance.pk_instance.spk = self.cleaned_data.get('spk_instance')
        self.instance.pk_instance.end_date = self.cleaned_data.get('end_date_pk')
        return super().save(commit=commit)

