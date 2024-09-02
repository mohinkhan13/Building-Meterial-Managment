from django.db import models

# Create your models here.


class User(models.Model):
    fname = models.CharField(max_length=180)
    lname = models.CharField(max_length=180)
    address = models.TextField()
    email = models.EmailField()
    mobile = models.PositiveIntegerField()
    password = models.CharField(max_length=128)
    profile_picture = models.FileField(upload_to="profile_picture/", default=" ")

    objects = models.Manager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # Custom exception if needed (though usually not required)
    class DoesNotExist(models.ObjectDoesNotExist):
        pass

    def __str__(self):
        return self.fname
