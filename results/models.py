from django.db import models


class Result(models.Model):
    title = models.CharField(max_length=200)
    examination = models.CharField(max_length=200)
    class_name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=50)
    result_file = models.FileField(upload_to='results/')
    published_date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = 'Result'
        verbose_name_plural = 'Results'

    def __str__(self):
        return self.title
