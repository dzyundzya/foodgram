# Generated by Django 3.2.16 on 2024-10-22 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20241021_1904'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'verbose_name': 'ингредиент рецепта', 'verbose_name_plural': 'Ингредиенты рецепта'},
        ),
    ]
