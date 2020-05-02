from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.ForeignKey('geo.Country', verbose_name="país", null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Dados"
        verbose_name_plural = "Dados"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    user = instance
    # Ensure User has a Profile.
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=user)
        profile.save()
