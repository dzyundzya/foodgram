# Generated by Django 3.2.16 on 2024-10-30 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscribe',
            options={'verbose_name': 'подписку', 'verbose_name_plural': 'Подписки'},
        ),
    ]
