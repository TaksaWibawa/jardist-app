from django import forms
from jardist.models.material_models import Material
from jardist.models.task_models import SubTaskMaterial, SubTask
from django.db import transaction

class MaterialForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}), label='Nama Material')
    unit = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'unit'}), label='Satuan')

    class Meta:
        model = SubTaskMaterial
        fields = ['subtask', 'category', 'material_price', 'labor_price', 'rab_client_volume', 'rab_contractor_volume', 'realization_client_volume', 'realization_contractor_volume']
        widgets = {
            'subtask': forms.Select(attrs={'class': 'form-select', 'id': 'subtask'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'category'}),
            'material_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'material_price', 'min': 0}),
            'labor_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'labor_price', 'min': 0}),
            'rab_client_volume': forms.NumberInput(attrs={'class': 'form-control', 'id': 'rab_client_volume', 'min': 0}),
            'rab_contractor_volume': forms.NumberInput(attrs={'class': 'form-control', 'id': 'rab_contractor_volume', 'min': 0}),
            'realization_client_volume': forms.NumberInput(attrs={'class': 'form-control', 'id': 'realization_client_volume', 'min': 0}),
            'realization_contractor_volume': forms.NumberInput(attrs={'class': 'form-control', 'id': 'realization_contractor_volume', 'min': 0}),
        }
        labels = {
            'subtask': 'Sub Pekerjaan',
            'category': 'Kategori Material',
            'material_price': 'Harga Bahan',
            'labor_price': 'Harga Upah',
            'rab_client_volume': 'Vol. Client (RAB)',
            'rab_contractor_volume': 'Vol. Pemborong (RAB)',
            'realization_client_volume': 'Vol. Client (Realisasi)',
            'realization_contractor_volume': 'Vol. Pemborong (Realisasi)',
        }

    context_config = {
        'rab': {
            'exclude': ['realization_client_volume', 'realization_contractor_volume']
        },
        'realization': {
            'exclude': ['rab_client_volume', 'rab_contractor_volume']
        }
    }

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        self.context = kwargs.pop('context', 'rab')
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if task is not None:
            self.fields['subtask'].queryset = SubTask.objects.filter(task=task)

        config = self.context_config.get(self.context, {})
        exclude_fields = config.get('exclude', [])

        for field_name in exclude_fields:
            if field_name in self.fields:
                del self.fields[field_name]

        self.subtask_id = self.request.GET.get('subtask_id')
        self.material_id = self.request.GET.get('material_id')
        if self.material_id:
            self.is_update = True
            self.instance = SubTaskMaterial.objects.get(subtask_id=self.subtask_id, material_id=self.material_id)

            self.initial = {
                'subtask': self.instance.subtask,
                'category': self.instance.category,
                'material_price': self.instance.material_price,
                'labor_price': self.instance.labor_price,
                'rab_client_volume': self.instance.rab_client_volume,
                'rab_contractor_volume': self.instance.rab_contractor_volume,
                'realization_client_volume': self.instance.realization_client_volume,
                'realization_contractor_volume': self.instance.realization_contractor_volume,
                'name': self.instance.material.name,
                'unit': self.instance.material.unit,
            }

        else:
            self.is_update = False

    def clean(self):
        cleaned_data = super().clean()
        subtask = cleaned_data.get('subtask')
        category = cleaned_data.get('category')

        if not self.material_id and subtask is not None and category is not None:
            existing_material = SubTaskMaterial.objects.filter(subtask=subtask, category=category, material__name__iexact=self.cleaned_data['name']).exists()
            if existing_material:
                self.add_error('category', 'Material sudah ada pada sub pekerjaan ini')

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True, *args, **kwargs):
        if self.is_update:
            return super().save(commit=commit, *args, **kwargs)

        material_name = self.cleaned_data.get('name')
        material_unit = self.cleaned_data.get('unit')
        material, created = Material.objects.get_or_create(
            name=material_name,
            defaults={'unit': material_unit}
        )

        self.instance.material = material
        self.instance.is_additional = True if self.context == 'realization' else False
        

        return super().save(commit=commit, *args, **kwargs)