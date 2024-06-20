from django.db import models
from .base_models.audit_model import Auditable

class Department(Auditable):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Departemen'
        verbose_name_plural = 'Departemen'

    def __str__(self):
        return self.name

class Role(Auditable):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Peran'
        verbose_name_plural = 'Peran'

    def __str__(self):
        return self.name