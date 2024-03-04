from django.db import models
from pytz import timezone

class Customer(models.Model):
    PRECEDENCE_TYPE = [
        ("Pri","Primary"),
        ("Sec","Secondary"),
    ]
    id = models.AutoField(primary_key=True)
    phoneNumber = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    linkedId = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    linkPrecedence = models.CharField(max_length=3, choices=PRECEDENCE_TYPE, default="Pri")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deletedAt = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id)    

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deletedAt = timezone.now()
        self.save(update_fields=['is_deleted', 'deletedAt'])
