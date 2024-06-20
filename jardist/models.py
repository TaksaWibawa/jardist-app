import uuid
from django.db import models, transaction
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL, editable=False)
    last_updated_at = models.DateTimeField(auto_now=True, editable=False)
    last_updated_by = models.ForeignKey(User, related_name='updated_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL, editable=False)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.created_by is None:
                self.created_by = User.objects.get(username='admin')
            if self.last_updated_by is None:
                self.last_updated_by = User.objects.get(username='admin')

        else:
            if self.last_updated_by is None:
                self.last_updated_by = User.objects.get(username='admin')
        super().save(*args, **kwargs)

class Department(Auditable):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class Role(Auditable):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class UserProfile(Auditable):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username
    
class SPK(Auditable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spk_number = models.CharField(max_length=100, unique=True, verbose_name='Nomor SPK')
    start_date = models.DateField(verbose_name='Tanggal Mulai')
    end_date = models.DateField(verbose_name='Tanggal Selesai')
    execution_time = models.IntegerField(verbose_name='Waktu Pelaksanaan')
    maintenance_time = models.IntegerField(verbose_name='Waktu Pemeliharaan')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    is_without_pk = models.BooleanField(default=False, verbose_name='Tanpa PK')

    class Meta:
        verbose_name = 'Surat Perjanjian Kerja'
        verbose_name_plural = 'Surat Perjanjian Kerja'
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.spk_number.startswith('SPK-'):
            self.spk_number = 'SPK-' + self.spk_number
        if self.execution_time is not None:
            self.end_date = self.start_date + timedelta(days=self.execution_time)
        super().save(*args, **kwargs)

        if self.is_without_pk:
            PK.objects.create(
                pk_number=self.spk_number, 
                spk=self, 
                start_date=self.start_date,
                end_date=self.end_date,
                execution_time=self.execution_time,
                maintenance_time=self.maintenance_time,
                status='PENGERJAAN'
            )

    def __str__(self):
        return self.spk_number
    
class PK(Auditable):
    STATUS_CHOICES = [
        ('PENGERJAAN', 'Pengerjaan'),
        ('PROSES_KTK', 'Proses KTK'),
        ('PEMBAYARAN', 'Pembayaran'),
        ('PEMELIHARAAN', 'Pemeliharaan'),
        ('SELESAI', 'Selesai'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pk_number = models.CharField(max_length=100, verbose_name='Nomor PK', unique=True)
    spk = models.ForeignKey(SPK, on_delete=models.CASCADE, verbose_name='SPK')
    start_date = models.DateField(verbose_name='Tanggal Mulai')
    end_date = models.DateField(verbose_name='Tanggal Selesai')
    execution_time = models.IntegerField(verbose_name='Waktu Pelaksanaan')
    maintenance_time = models.IntegerField(verbose_name='Waktu Pemeliharaan')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENGERJAAN', verbose_name='Status PK')

    class Meta:
        verbose_name = 'Perintah Kerja'
        verbose_name_plural = 'Perintah Kerja'

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _('End date must be later than start date.')
            })

        if self.execution_time and self.execution_time < 0:
            raise ValidationError({
                'execution_time': _('Execution time must be a positive number.')
            })

        if self.maintenance_time and self.maintenance_time < 0:
            raise ValidationError({
                'maintenance_time': _('Maintenance time must be a positive number.')
            })

    def save(self, *args, **kwargs):
        if self.pk is not None and PK.objects.filter(pk=self.pk).exists():
            old_pk = PK.objects.get(pk=self.pk)
            if self.status != old_pk.status:
                PKStatusAudit.objects.create(
                    pk_instance=self,
                    old_status=old_pk.status,
                    new_status=self.status,
                    changed_by=self.last_updated_by
                )

        if not self.spk.is_without_pk:
            if not self.pk_number.startswith('PK-'):
                self.pk_number = 'PK-' + self.pk_number
        else:
            self.pk_number = self.spk.spk_number

        if self.execution_time is not None:
            self.end_date = self.start_date + timedelta(days=self.execution_time)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.pk_number
 
class PKStatusAudit(Auditable):
    pk_instance = models.ForeignKey(PK, on_delete=models.CASCADE, related_name='status_changes', verbose_name='No. PK')
    old_status = models.CharField(max_length=20, choices=PK.STATUS_CHOICES, verbose_name='Status Lama')
    new_status = models.CharField(max_length=20, choices=PK.STATUS_CHOICES, verbose_name='Status Baru')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Diubah Oleh')

    class Meta:
        verbose_name = 'Riwayat Perubahan Status PK'
        verbose_name_plural = 'Riwayat Perubahan Status PK'

    def __str__(self):
        return f'{self.pk_instance.pk_number} - {self.old_status} -> {self.new_status}'