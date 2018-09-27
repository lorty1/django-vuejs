# Generated by Django 2.1 on 2018-08-23 15:17

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pager', '0002_blockmedia_header'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='page',
            field=mptt.fields.TreeForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pages', to='pager.Page', verbose_name='page'),
        ),
        migrations.AlterField(
            model_name='blockmedia',
            name='block',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pager.Block'),
        ),
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='pager.Page', verbose_name='parent page'),
        ),
    ]