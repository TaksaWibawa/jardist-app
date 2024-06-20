from django.db import models
from django.contrib.auth.models import User

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