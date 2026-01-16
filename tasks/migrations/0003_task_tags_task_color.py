# Generated manually for Lead Developer Level features

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task_description_task_due_date_task_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags (e.g., work, personal, urgent)', max_length=255, null=True, verbose_name='Tags', db_index=True),
        ),
        migrations.AddField(
            model_name='task',
            name='color',
            field=models.CharField(blank=True, default='', help_text='Hex color code (e.g., #FF5733)', max_length=7, verbose_name='Color'),
        ),
    ]

