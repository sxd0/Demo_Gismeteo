from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    search_count = models.IntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} searched for {self.city}'
