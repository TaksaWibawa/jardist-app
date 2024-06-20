from django.db import models
from django.contrib.auth.models import User
from .role_models import Role, Department
from .base_models.audit_model import Auditable

class UserProfile(Auditable):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username