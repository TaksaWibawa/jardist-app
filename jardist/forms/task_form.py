import csv
from jardist.models.task_models import Task, TaskType
from jardist.models.task_models import SubTask, SubTaskType, SubTaskMaterial
from jardist.models.material_models import Material, MaterialCategory
from jardist.models.contract_models import PK
from jardist.constants import TASK_FORM_FIELDS
from django.db import transaction
from django import forms

class TaskForm(forms.ModelForm):
    pk_instance = forms.ModelChoiceField(queryset=PK.objects.all(), empty_label='Pilih No. PK', widget=forms.Select(attrs={'class': 'form-control', 'id': 'pk_instance'}), label='No. PK')
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.all(), empty_label='Pilih Jenis Pekerjaan', widget=forms.Select(attrs={'class': 'form-control', 'id': 'task_type'}), label='Jenis Pekerjaan')

    class Meta:
        model = Task
        fields = ['task_name', 'customer_name', 'location', 'pk_instance', 'task_type', 'execution_time', 'maintenance_time', 'rab', 'is_with_template']
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'task_name', 'placeholder': 'Isi Nama Pekerjaan'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'customer_name', 'placeholder': 'Isi Nama Pelanggan'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location', 'placeholder': 'Isi Lokasi Pekerjaan'}),
            'execution_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'execution_time', 'min': 0, 'placeholder': 'Terisi Otomatis Berdasarkan PK'}),
            'maintenance_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'maintenance_time', 'min': 0, 'placeholder': 'Isi Masa Pemeliharaan Dalam Hari Kalender'}),
            'rab': forms.FileInput(attrs={'class': 'form-control', 'id': 'rab', 'accept': '.csv', 'placeholder': 'Pilih File RAB'}),
            'is_with_template': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_with_template', 'placeholder': 'Centang jika pakai template RAB'}),
        }
        labels = {
            'task_name': 'Nama Pekerjaan',
            'customer_name': 'Nama Pelanggan',
            'location': 'Lokasi Pekerjaan',
            'execution_time': 'Waktu Pelaksanaan',
            'maintenance_time': 'Waktu Pemeliharaan',
            'rab': 'Upload RAB',
            'is_with_template': 'Centang jika pakai template RAB',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.is_create_page = kwargs.pop('is_create_page', False)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        is_with_template = cleaned_data.get('is_with_template')
        rab = cleaned_data.get('rab')
        task_type = cleaned_data.get('task_type')

        if not rab:
            self.add_error('rab', "File RAB tidak boleh kosong.")
        elif not rab.name.endswith('.csv'):
            self.add_error('rab', "File RAB harus berformat CSV.")
        else:
            rab.seek(0)
            reader = csv.reader(rab.read().decode('utf-8').splitlines())
            headers = next(reader, None)
            required_headers = TASK_FORM_FIELDS
            if headers != required_headers:
                self.add_error('rab', "File RAB tidak sesuai dengan format RAB.")
            else:
                task_type_found = any(jenis_pekerjaan.lower() == task_type.name.lower() for jenis_pekerjaan, *_ in reader)
                if not task_type_found:
                    self.add_error('task_type', 'Jenis Pekerjaan tidak ditemukan dalam file RAB')

        if not is_with_template:
            return cleaned_data

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit=False)
    
        rab = self.cleaned_data.get('rab')
        rab.seek(0)
        reader = csv.reader(rab.read().decode('utf-8').splitlines())
        next(reader, None)
    
        if not self.is_create_page:
            SubTask.objects.filter(task=instance).delete()
    
        for row in reader:
            jenis_pekerjaan, sub_jenis_pekerjaan, kategori_material, nama_material, satuan, bahan, upah, vol_pln, vol_pemb = row
    
            task_type = TaskType.objects.filter(name__iexact=jenis_pekerjaan).first()
    
            if task_type and task_type == instance.task_type:
                sub_task_type, created = SubTaskType.objects.get_or_create(name__iexact=sub_jenis_pekerjaan, defaults={'name': sub_jenis_pekerjaan})
                if created:
                    sub_task_type.task_types.add(task_type)
                material_category, _ = MaterialCategory.objects.get_or_create(name__iexact=kategori_material, defaults={'name': kategori_material})
                material, _ = Material.objects.get_or_create(name__iexact=nama_material, defaults={'name': nama_material, 'category': material_category, 'unit': satuan,    'price': bahan})
    
                sub_task, created = SubTask.objects.get_or_create(task=instance, sub_task_type=sub_task_type)
                SubTaskMaterial.objects.create(subtask=sub_task, material=material, labor_price=upah, client_volume=vol_pln, contractor_volume=vol_pemb)
    
        instance.save()
        return instance