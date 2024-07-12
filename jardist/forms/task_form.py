from django import forms
from django.db import transaction
from jardist.constants import TASK_FORM_FIELDS
from jardist.models.contract_models import PK
from jardist.models.material_models import Material, MaterialCategory
from jardist.models.task_models import SubTask, SubTaskType, SubTaskMaterial, TemplateRAB
from jardist.models.task_models import Task, TaskType
from jardist.utils import clean_decimal_field
import csv

class TaskForm(forms.ModelForm):
    pk_instance = forms.ModelChoiceField(queryset=PK.objects.all(), empty_label='Pilih No. PK', widget=forms.Select(attrs={'class': 'form-select', 'id': 'pk_instance'}), label='No. PK')
    task_type = forms.ModelChoiceField(queryset=TaskType.objects.all(), empty_label='Pilih Jenis Pekerjaan', widget=forms.Select(attrs={'class': 'form-select', 'id': 'task_type'}), label='Jenis Pekerjaan')
    is_with_template = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'is_with_template', 'placeholder': 'Centang jika pakai template RAB'}), label='Centang jika pakai template RAB')

    class Meta:
        model = Task
        fields = ['task_name', 'customer_name', 'location', 'pk_instance', 'task_type', 'execution_time', 'maintenance_time', 'rab']
        widgets = {
            'task_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'task_name', 'placeholder': 'Isi Nama Pekerjaan'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'customer_name', 'placeholder': 'Isi Nama Pelanggan'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location', 'placeholder': 'Isi Lokasi Pekerjaan'}),
            'execution_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'execution_time', 'min': 0, 'placeholder': 'Terisi Otomatis Berdasarkan PK'}),
            'maintenance_time': forms.NumberInput(attrs={'class': 'form-control', 'id': 'maintenance_time', 'min': 0, 'placeholder': 'Isi Masa Pemeliharaan Dalam Hari Kalender'}),
            'rab': forms.FileInput(attrs={'class': 'form-control', 'id': 'rab', 'accept': '.csv', 'placeholder': 'Pilih File RAB'}),
        }
        labels = {
            'task_name': 'Nama Pekerjaan',
            'customer_name': 'Nama Pelanggan',
            'location': 'Lokasi Pekerjaan',
            'execution_time': 'Waktu Pelaksanaan',
            'maintenance_time': 'Waktu Pemeliharaan',
            'rab': 'Upload RAB',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.is_create_page = kwargs.pop('is_create_page', False)
        pk_id = kwargs.pop('pk_id', None)
        super().__init__(*args, **kwargs)

        if self.is_create_page:
            try:
                pk_instance = PK.objects.get(id=pk_id)
                self.fields['pk_instance'].initial = pk_instance
                self.fields['execution_time'].initial = pk_instance.execution_time
            except PK.DoesNotExist:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        is_with_template = cleaned_data.get('is_with_template')
        rab = cleaned_data.get('rab')
        task_type = cleaned_data.get('task_type')

        if is_with_template:
            return cleaned_data

        if not rab:
            self.add_error('rab', "File RAB tidak boleh kosong.")
        elif not (rab.name.endswith('.csv') or rab.name.endswith('.txt')):
            self.add_error('rab', "File RAB harus berformat CSV atau TXT.")
        else:
            rab.seek(0)
            sample = rab.read(1024).decode('utf-8')
            rab.seek(0)
            comma_count = sample.count(',')
            semicolon_count = sample.count(';')

            delimiter = ',' if comma_count > semicolon_count else ';'

            reader = csv.reader(rab.read().decode('utf-8').splitlines(), delimiter=delimiter, quotechar='"')
            headers = next(reader)
            required_headers = TASK_FORM_FIELDS

            if headers != required_headers:
                print(headers,delimiter)
                self.add_error('rab', "File RAB tidak sesuai dengan format RAB.")
            else:
                task_type_found = False
                for row in reader:
                    if row[headers.index('Jenis Pekerjaan')].strip().lower() == task_type.name.lower():
                        task_type_found = True
                        break
                if not task_type_found:
                    self.add_error('task_type', 'Jenis Pekerjaan tidak ditemukan dalam file RAB')

        return cleaned_data
    

    @transaction.atomic
    def save(self, commit=True):
        # if any fields are not changed, return back the instance
        if not self.has_changed() and not self.is_create_page:
            if self.instance is not None:
                return self.instance
            else:
                # Handle the case where self.instance is None
                instance = super().save(commit=False)
                if commit:
                    instance.save()
                return instance

        instance = super().save(commit=False)

        is_with_template = self.cleaned_data.get('is_with_template')
        task_type = self.cleaned_data.get('task_type')

        try:
            # if on create task is_with_template is checked, use template rab file. Otherwise, use uploaded rab file
            if is_with_template and self.is_create_page:
                template_file = TemplateRAB.objects.filter(task_type=task_type).first()
                if template_file:
                    instance.rab = template_file.rab
                    instance.rab.seek(0)
                    sample = instance.rab.read(1024).decode('utf-8')
                    instance.rab.seek(0)
                    comma_count = sample.count(',')
                    semicolon_count = sample.count(';')

                    delimiter = ',' if comma_count > semicolon_count else ';'
                    
                    reader = csv.reader(instance.rab.read().decode('utf-8').splitlines(), delimiter=delimiter, quotechar='"')
                    headers = next(reader)
                else:
                    self.add_error('task_type', 'Template RAB tidak ditemukan')
                    return None
            else:
                rab = self.cleaned_data.get('rab')
                if rab:
                    rab.seek(0)
                    sample = rab.read(1024).decode('utf-8')
                    rab.seek(0)
                    comma_count = sample.count(',')
                    semicolon_count = sample.count(';')

                    delimiter = ',' if comma_count > semicolon_count else ';'

                    reader = csv.reader(rab.read().decode('utf-8').splitlines(), delimiter=delimiter, quotechar='"')
                    headers = next(reader)
                else:
                    self.add_error('rab', 'File RAB tidak ditemukan')
                    return None

            # if rab file is changed and not on create page, delete all sub tasks
            if not self.is_create_page and 'rab' in self.changed_data:
                SubTask.objects.filter(task=instance).delete()

            if commit:
                instance.save()

            # if rab file is changed or on create page, create sub tasks and sub task materials
            if 'rab' in self.changed_data or self.is_create_page:
                sub_tasks_to_create = []
                sub_task_materials_to_create = []

                # preserve task types, sub task types, and materials in memory
                task_types = list(TaskType.objects.all())
                sub_task_types = list(SubTaskType.objects.all())
                materials = list(Material.objects.all())

                # iterate over the rows in the csv file
                for row in reader:
                    jenis_pekerjaan, sub_jenis_pekerjaan, kategori_material, nama_material, satuan, bahan, upah, vol_pln, vol_pemb = row

                    bahan, upah, vol_pln, vol_pemb = map(clean_decimal_field, [bahan, upah, vol_pln, vol_pemb])

                    # check first for task type
                    task_type = next((tt for tt in task_types if tt.name.lower() == jenis_pekerjaan.lower()), None)

                    # if task type is found, create sub task and sub task materials
                    if task_type and task_type == instance.task_type:
                        # check if sub task type already exists, if not create new
                        sub_task_type = next((stt for stt in sub_task_types if stt.name.lower() == sub_jenis_pekerjaan.lower()), None)
                        if not sub_task_type:
                            sub_task_type = SubTaskType.objects.create(name=sub_jenis_pekerjaan)
                            sub_task_type.task_types.add(task_type)
                            sub_task_types.append(sub_task_type)

                        # check if material already exists, if not create new
                        material = next((m for m in materials if m.name.lower() == nama_material.lower()), None)
                        if not material:
                            material = Material.objects.create(name=nama_material, unit=satuan)
                            materials.append(material)

                        # create sub task and sub task materials
                        sub_task, created = SubTask.objects.get_or_create(task=instance, sub_task_type=sub_task_type)
                        sub_task_materials_to_create.append(SubTaskMaterial(
                            subtask=sub_task, 
                            material=material, 
                            material_price=bahan,
                            labor_price=upah, 
                            rab_client_volume=vol_pln, 
                            rab_contractor_volume=vol_pemb, 
                            category=MaterialCategory.objects.get(name__iexact=kategori_material)))

                # do bulk create for sub tasks and sub task materials
                SubTask.objects.bulk_create(sub_tasks_to_create)
                SubTaskMaterial.objects.bulk_create(sub_task_materials_to_create)
            
        except Exception as e:
            self.add_error('rab', 'Error reading RAB file: ' + str(e))
            transaction.set_rollback(True)
            return None
        
        return instance