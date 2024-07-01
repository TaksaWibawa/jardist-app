from django.db import models
from .base_models.audit_model import Auditable

class MaterialCategory(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Nama Kategori Material')
    description = models.CharField(max_length=200, null=True, blank=True, verbose_name='Deskripsi')

    class Meta:
        verbose_name = 'Kategori Material'
        verbose_name_plural = 'Kategori Material'

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        return super(MaterialCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Material(Auditable):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Nama Material')
    unit = models.CharField(max_length=100, verbose_name='Satuan Material')

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Material'

    def __str__(self):
        return self.name