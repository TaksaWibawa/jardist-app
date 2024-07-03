import uuid
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import timedelta
from .role_models import Department
from .base_models.audit_model import Auditable

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
        if self.execution_time is not None:
            self.end_date = self.start_date + timedelta(days=self.execution_time)
        super().save(*args, **kwargs)

        if self.is_without_pk and not PK.objects.filter(spk=self).exists():
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
    bast_date = models.DateField(null=True, blank=True, verbose_name='Tanggal BAST I')
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
        # Check if the instance is being updated
        if not self._state.adding:
            with transaction.atomic():
                old_pk = PK.objects.select_for_update().get(pk=self.pk)
                if self.status != old_pk.status:
                    PKStatusAudit.objects.create(
                        pk_instance=self,
                        old_status=old_pk.status,
                        new_status=self.status,
                        changed_by=self.last_updated_by
                    )
        if self.execution_time is not None and self.start_date is not None:
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
    
class PKArchiveDocument(Auditable):
    pk_instance = models.ForeignKey(PK, on_delete=models.CASCADE, related_name='archive_documents', verbose_name=_('Perintah Kerja'))

    class Meta:
        verbose_name = _('Dokumen Arsip PK')
        verbose_name_plural = _('Dokumen Arsip PK')

    def __str__(self):
        return f"{self.pk_instance.pk_number}"

class Document(Auditable):
    pk_archive = models.ForeignKey(PKArchiveDocument, on_delete=models.CASCADE, related_name='documents', verbose_name=_('Dokumen Arsip PK'))
    pickup_file = models.FileField(upload_to='static/jardist/files/pk_archive/pickup/', verbose_name=_('File Dokumen Pengambilan Barang'))
    pickup_description = models.CharField(max_length=255, verbose_name=_('Deskripsi Dokumen Pengambilan Barang'))
    proof_file = models.FileField(upload_to='static/jardist/files/pk_archive/proof/', verbose_name=_('File Bukti Pengambilan Barang'), null=True, blank=True)
    proof_description = models.CharField(max_length=255, verbose_name=_('Deskripsi Bukti Pengambilan Barang'), null=True, blank=True)

    class Meta:
        verbose_name = _('Dokumen')
        verbose_name_plural = _('Dokumen')

    def __str__(self):
        file_name = self.pickup_file.name if self.pickup_file else self.proof_file.name if self.proof_file else 'No File'
        return f"{self.pk_archive.pk_instance.pk_number} - {file_name}"