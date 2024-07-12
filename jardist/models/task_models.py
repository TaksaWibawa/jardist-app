import uuid
import csv
from jardist.constants import TASK_FORM_FIELDS
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from .material_models import Material, MaterialCategory
from .contract_models import PK
from .base_models.audit_model import Auditable

class TaskType(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Jenis Pekerjaan')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Jenis Pekerjaan'
        verbose_name_plural = 'Jenis Pekerjaan'

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class SubTaskType(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Sub Jenis Pekerjaan')
    task_types = models.ManyToManyField(TaskType, related_name='sub_task_types', verbose_name='Jenis Pekerjaan')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Sub Jenis Pekerjaan'
        verbose_name_plural = 'Sub Jenis Pekerjaan'

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Task(Auditable):
    STATUS_CHOICES = (
        ('On Progress', 'On Progress'),
        ('Done', 'Done'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=100, verbose_name='Nama Pekerjaan')
    pk_instance = models.ForeignKey(PK, on_delete=models.CASCADE, verbose_name='No. PK', related_name='tasks')
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE, verbose_name='Jenis Pekerjaan')
    customer_name = models.CharField(max_length=100, verbose_name='Nama Pelanggan')
    location = models.CharField(max_length=100, verbose_name='Lokasi Pekerjaan')
    execution_time = models.IntegerField(verbose_name='Waktu Pelaksanaan')
    maintenance_time = models.IntegerField(verbose_name='Waktu Pemeliharaan')
    rab = models.FileField(upload_to='rab/', null=True, blank=True, verbose_name='RAB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Progress', verbose_name='Status')

    class Meta:
        verbose_name = 'Pekerjaan'
        verbose_name_plural = 'Pekerjaan'

    def clean(self):
        super().clean()

        if self.execution_time and self.execution_time < 0:
            raise ValidationError({
                'execution_time': _('Execution time must be a positive number.')
            })

        if self.maintenance_time and self.maintenance_time < 0:
            raise ValidationError({
                'maintenance_time': _('Maintenance time must be a positive number.')
            })

        if self.rab:
            if not self.rab.name.endswith('.csv'):
                raise ValidationError("File RAB harus berformat CSV.")
    
            try:
                self.rab.seek(0)
                sample = self.rab.read(1024).decode('utf-8')
                self.rab.seek(0)
                comma_count = sample.count(',')
                semicolon_count = sample.count(';')

                delimiter = ',' if comma_count > semicolon_count else ';'
                reader = csv.reader(self.rab.read().decode('utf-8').splitlines(), delimiter=delimiter, quotechar='"')
                headers = next(reader, None)
                required_headers = TASK_FORM_FIELDS
                if headers != required_headers:
                    raise ValidationError("File RAB tidak sesuai dengan template.")
            except Exception as e:
                raise ValidationError(f"Error reading RAB file: {str(e)}")
        
    def __str__(self):
        return self.task_name

class SubTask(Auditable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Pekerjaan')
    sub_task_type = models.ForeignKey(SubTaskType, on_delete=models.CASCADE, verbose_name='Sub Jenis Pekerjaan')
    materials = models.ManyToManyField(Material, through='SubTaskMaterial')

    class Meta:
        verbose_name = 'Sub Pekerjaan'
        verbose_name_plural = 'Sub Pekerjaan'

    def __str__(self):
        return self.sub_task_type.name

class SubTaskMaterial(models.Model):
    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE, verbose_name='Kategori Material', default=1)
    material_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Harga Bahan', null=True, blank=True)
    labor_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Harga Upah', null=True, blank=True)
    rab_client_volume = models.IntegerField(verbose_name='Volume Client (RAB)', null=True, blank=True, default=0)
    rab_contractor_volume = models.IntegerField(verbose_name='Volume Pemborong (RAB)', null=True, blank=True, default=0)
    realization_client_volume = models.IntegerField(verbose_name='Volume Client (Realisasi)', null=True, blank=True, default=0)
    realization_contractor_volume = models.IntegerField(verbose_name='Volume Pemborong (Realisasi)', null=True, blank=True, default=0)
    is_additional = models.BooleanField(default=False, verbose_name='Kerja Tambah')

    class Meta:
        verbose_name = 'Material Sub Pekerjaan'
        verbose_name_plural = 'Material Sub Pekerjaan'

    def __str__(self):
        return self.material.name

class TemplateRAB(Auditable):
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE, verbose_name='Jenis Pekerjaan')
    rab = models.FileField(upload_to='rab/', verbose_name='Template RAB', help_text='Upload file RAB dalam format CSV')

    class Meta:
        verbose_name = 'Template RAB'
        verbose_name_plural = 'Template RAB'

    def clean(self):
        if not self.rab.name.endswith('.csv'):
            raise ValidationError("File RAB harus berformat CSV.")
        
        if TemplateRAB.objects.filter(task_type=self.task_type).exclude(id=self.id).exists():
            raise ValidationError("Template RAB untuk jenis pekerjaan ini sudah ada.")

    def __str__(self):
        return self.task_type.name
    
class TaskDocumentation(Auditable):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='documentations', verbose_name='Pekerjaan')
    location = models.CharField(max_length=255, verbose_name='Lokasi')

    class Meta:
        verbose_name = 'Dokumentasi Pekerjaan'
        verbose_name_plural = 'Dokumentasi Pekerjaan'

    def __str__(self):
        return f"{self.task.task_name} - {self.location}"

class TaskDocumentationPhoto(Auditable):
    task_documentation = models.ForeignKey(TaskDocumentation, on_delete=models.CASCADE, related_name='photos', verbose_name='Dokumentasi Pekerjaan')
    photo = models.FileField(upload_to='task_documentation/', verbose_name='Foto')
    description = models.CharField(max_length=255, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Foto Dokumentasi Pekerjaan'
        verbose_name_plural = 'Foto Dokumentasi Pekerjaan'

    def __str__(self):
        return f"{self.task_documentation.task.task_name} - {self.description}"