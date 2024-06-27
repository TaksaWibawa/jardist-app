from django import forms
from jardist.models.task_models import SubTaskMaterial

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

    def __init__(self, *args, **kwargs):
        show_type = kwargs.pop('show_type', 'rab')
        super().__init__(*args, **kwargs)

        if show_type == 'rab':
            print(show_type)
            del self.fields['realization_client_volume']
            del self.fields['realization_contractor_volume']
        else:
            del self.fields['rab_client_volume']
            del self.fields['rab_contractor_volume']

class BaseSubTaskMaterialFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial', [])
        self.show_type = kwargs.pop('show_type', 'rab')
        print(self.show_type)
        super().__init__(*args, **kwargs)

        for form, initial in zip(self.forms, initial_data):
            form.show_type = self.show_type
            if self.show_type == 'rab':
                form.initial['rab_client_volume'] = initial.get('rab_client_volume', 0.00)
                form.initial['rab_contractor_volume'] = initial.get('rab_contractor_volume', 0.00)
            else:
                form.initial['realization_client_volume'] = initial.get('realization_client_volume', 0.00)
                form.initial['realization_contractor_volume'] = initial.get('realization_contractor_volume', 0.00)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['show_type'] = self.show_type
        return kwargs

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