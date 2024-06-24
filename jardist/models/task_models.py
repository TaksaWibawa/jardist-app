import uuid
import csv
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from .material_models import Material
from .contract_models import PK
from .base_models.audit_model import Auditable

class TaskType(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Jenis Pekerjaan')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Jenis Pekerjaan'
        verbose_name_plural = 'Jenis Pekerjaan'

    def __str__(self):
        return self.name
    
class SubTaskType(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Sub Jenis Pekerjaan')
    task_types = models.ManyToManyField(TaskType, related_name='sub_task_types', verbose_name='Jenis Pekerjaan')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Sub Jenis Pekerjaan'
        verbose_name_plural = 'Sub Jenis Pekerjaan'

    def __str__(self):
        return self.name

class Task(Auditable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=100, verbose_name='Nama Pekerjaan')
    pk_instance = models.ForeignKey(PK, on_delete=models.CASCADE, verbose_name='No. PK')
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE, verbose_name='Jenis Pekerjaan')
    customer_name = models.CharField(max_length=100, verbose_name='Nama Pelanggan')
    location = models.CharField(max_length=100, verbose_name='Lokasi Pekerjaan')
    execution_time = models.IntegerField(verbose_name='Waktu Pelaksanaan')
    maintenance_time = models.IntegerField(verbose_name='Waktu Pemeliharaan')
    is_with_template = models.BooleanField(default=False, verbose_name='Dengan Template RAB')
    rab = models.FileField(upload_to='static/jardist/files/rab/', null=True, blank=True, verbose_name='RAB')

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

        if self.is_with_template and self.rab:
            if not self.rab.name.endswith('.csv'):
                raise ValidationError("File RAB harus berformat CSV.")

            self.rab.seek(0)
            reader = csv.reader(self.rab.read().decode('utf-8').splitlines())
            headers = next(reader, None)
            required_headers = ['Jenis Pekerjaan', 'Sub Jenis Pekerjaan', 'Kategori Material', 'Nama Material', 'Satuan Material', 'Harga Bahan', 'Harga Upah', 'Volume Client', 'Volume Pemborong']
            if headers != required_headers:
                raise ValidationError("File RAB tidak sesuai dengan template.")
        
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
    labor_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Harga Upah')
    # rab
    client_volume = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Volume Client')
    contractor_volume = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Volume Pemborong')
    # realization

    class Meta:
        unique_together = ('subtask', 'material')

    def __str__(self):
        return self.material.name