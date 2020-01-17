# -*- coding: utf-8 -*-

# Create your models here.
from django.db import models


class RedEvent(models.Model):
    event_text = models.CharField(max_length=200)
    # YYYY-MM-DD format
    event_date = models.DateField()

    def __str__(self):
        return self.event_text
