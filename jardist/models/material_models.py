from django.db import models
from .base_models.audit_model import Auditable

class MaterialCategory(Auditable):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='Nama Kategori Material')

    class Meta:
        verbose_name = 'Kategori Material'
        verbose_name_plural = 'Kategori Material'

    def __str__(self):
        return self.name

class Material(Auditable):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Nama Material')
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE, verbose_name='Kategori Material')
    unit = models.CharField(max_length=100, verbose_name='Satuan Material')
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Harga Bahan')

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Material'

    def __str__(self):
        return self.name