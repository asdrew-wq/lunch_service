from django.db import models

# The standard User model is used for the employee and restaurant owner
from django.contrib.auth.models import User


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    content = models.JSONField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('restaurant', 'date')  # One restaurant can offer one menu per day

    def __str__(self):
        return f"{self.restaurant} - {self.date}"


class Vote(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')  # An employee can vote once per day

    def __str__(self):
        return f"{self.employee} voted for {self.menu}"
