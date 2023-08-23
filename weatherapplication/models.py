from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

        
class Login(models.Model):
    usernameoremail = models.CharField(max_length=100, default='Not Applicable', error_messages={'required': 'Please enter your username or email.',
                                                                       'invalid': 'Please enter a valid username or email.'})
    password = models.CharField(max_length=20, error_messages={'required': 'Please enter your password.',
                                'invalid': 'Please enter a valid password.', 'missing': 'Please enter your password.',
                                'mismatch': 'The password you entered is incorrect.',
                                'none': 'Please enter your the correct details.'})
    
    def save(self, *args, **kwargs):
        if '@' in self.usernameoremail:
            self.email = self.usernameoremail
        else:
            self.username = self.usernameoremail
        
        super().save(*args, **kwargs)

class Feedback(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
