import csv
from jardist.models.task_models import Task, TaskType
from jardist.models.contract_models import PK
from jardist.constants import TASK_FORM_FIELDS
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

    def clean_rab(self):
        rab = self.cleaned_data.get('rab')

        if not rab:
            raise forms.ValidationError("File RAB tidak boleh kosong.")

        if not rab.name.endswith('.csv'):
            raise forms.ValidationError("File RAB harus berformat CSV.")

        return rab
    
    def clean(self):
        cleaned_data = super().clean()
        rab = cleaned_data.get('rab')
        is_with_template = cleaned_data.get('is_with_template')

        if not rab:
            self.add_error('rab', "File RAB tidak boleh kosong.")
        elif not rab.name.endswith('.csv'):
            self.add_error('rab', "File RAB harus berformat CSV.")

        rab.seek(0)
        reader = csv.reader(rab.read().decode('utf-8').splitlines())
        headers = next(reader, None)
        required_headers = TASK_FORM_FIELDS
        if headers != required_headers:
            self.add_error('rab', "File RAB tidak sesuai dengan format RAB.")