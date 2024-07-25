# Generated by Django 4.1.7 on 2024-07-25 11:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0001_initial'),
        ('mqtt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NodeACL',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('access_level', models.IntegerField(choices=[(0, 'GET'), (1, 'POST'), (2, 'MOD'), (3, 'POP')], default=0, verbose_name='access level')),
                ('device', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='devices.device')),
                ('topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mqtt.topic')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
