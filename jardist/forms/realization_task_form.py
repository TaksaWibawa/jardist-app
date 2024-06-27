from django import forms
from jardist.models.task_models import SubTaskMaterial
from jardist.models.contract_models import SPK
from jardist.models.task_models import Task

TASK_STATUS_CHOICES = [
    ('', 'Pilih Status Pekerjaan'),
    ('On Progress', 'On Progress'),
    ('Done', 'Done'),
]


class RealizationTaskForm(forms.ModelForm):
    spk_instance = forms.ModelChoiceField(queryset=SPK.objects.all(), empty_label='Pilih No. SPK', widget=forms.Select(attrs={'class': 'form-control', 'id': 'spk_instance'}), label='No. SPK')
    end_date_pk = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'id': 'end_date_pk', 'type': 'date'}), label='Tanggal Berakhir PK')

    class Meta:
        model = Task
        fields = ['pk_instance', 'location', 'customer_name', 'task_type', 'status']
        widgets = {
            'pk_instance': forms.Select(attrs={'class': 'form-control', 'id': 'pk_instance', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'customer_name'}),
            'task_type': forms.Select(attrs={'class': 'form-control', 'id': 'task_type'}),
            'status': forms.Select(choices=TASK_STATUS_CHOICES, attrs={'class': 'form-control', 'id': 'status'}),
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

class SubTaskMaterialForm(forms.ModelForm):
    class Meta:
        model = SubTaskMaterial
        fields = ['realization_client_volume', 'realization_contractor_volume', 'rab_client_volume', 'rab_contractor_volume']
        widgets = {
            'realization_client_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'realization_contractor_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'rab_client_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'rab_contractor_volume': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BaseSubTaskMaterialFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial', [])
        super().__init__(*args, **kwargs)

        for form, initial in zip(self.forms, initial_data):
            form.initial['realization_client_volume'] = initial.get('realization_client_volume', 0.00)
            form.initial['realization_contractor_volume'] = initial.get('realization_contractor_volume', 0.00)
            form.initial['rab_client_volume'] = initial.get('rab_client_volume', 0.00)
            form.initial['rab_contractor_volume'] = initial.get('rab_contractor_volume', 0.00)

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            if self.has_changed():
                instance.save()
        if commit:
            for instance in instances:
                self.save_m2m()
        return instances
        
SubTaskMaterialFormSet = forms.modelformset_factory(
    SubTaskMaterial, 
    form=SubTaskMaterialForm, 
    formset=BaseSubTaskMaterialFormSet,
    extra=0,
)

