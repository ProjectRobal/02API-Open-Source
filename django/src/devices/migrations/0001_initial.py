# Generated by Django 4.1.7 on 2024-07-25 11:59

import devices.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('last_login_date', models.DateTimeField(blank=True, null=True)),
                ('key', models.CharField(default=devices.models.gen_key, max_length=32, unique=True)),
                ('status', models.IntegerField(choices=[(0, 'AVAILABLE'), (1, 'BUSY'), (2, 'FAULTY'), (3, 'SHUTDOWN')], default=0)),
                ('major_version', models.PositiveIntegerField()),
                ('minor_version', models.PositiveIntegerField()),
                ('patch_version', models.PositiveIntegerField()),
            ],
            options={
                'permissions': [('device_view', 'Can access device page'), ('device_user', 'Can create other users with device admin'), ('device_add', 'Can add devices'), ('device_rm', 'Can remove devices'), ('node_rm', 'Can remove node'), ('topic_rm', 'Can remove topic'), ('plugin_add', 'Can add plugins'), ('plugin_rm', 'Can remove plugins'), ('plugin_view', 'Can view plugins')],
            },
        ),
        migrations.CreateModel(
            name='TrashDevice',
            fields=[
                ('device_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='devices.device')),
            ],
            options={
                'abstract': False,
            },
            bases=('devices.device',),
        ),
    ]
