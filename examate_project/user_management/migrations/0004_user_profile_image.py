# Generated by Django 4.2.6 on 2024-04-18 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0003_alter_user_options_alter_otp_table_alter_user_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
