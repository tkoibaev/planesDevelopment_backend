from django.db import models

# Create your models here.

class Applications(models.Model):
    application_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)
    formed_at = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)
    moderator = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey('Users', models.DO_NOTHING, related_name='applications_customer_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'applications'


class Applicationscomponents(models.Model):
    application = models.OneToOneField(Applications, models.DO_NOTHING, primary_key=True)  # The composite primary key (application_id, option_id) found, that is not supported. The first column is selected.
    option = models.ForeignKey('Options', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'applicationscomponents'
        unique_together = (('application', 'option'),)


class Options(models.Model):
    option_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available = models.BooleanField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'options'


class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)
    is_moderator = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
