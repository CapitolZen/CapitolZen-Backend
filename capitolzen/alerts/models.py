from django.db import models


class Alert:

    user = models.ForeignKey('users.User',)
    message = models.TextField()

    def __str__(self):
        return self.message
