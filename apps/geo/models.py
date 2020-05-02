from django.db import models


class Country(models.Model):
    name = models.CharField(verbose_name="nome", max_length=100)
    slug = models.SlugField()
    flag = models.ImageField(verbose_name="bandeira", upload_to='countries', null=True, blank=True)

    class Meta:
        verbose_name = 'país'
        verbose_name_plural = 'países'
        ordering = ['name']

    def __str__(self):
        return self.name
