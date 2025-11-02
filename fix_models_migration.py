# Cloud server pe yeh migration create karo:

# 1. Migration generate karo
# python manage.py makemigrations HealthCheck_app

# 2. Migration apply karo  
# python manage.py migrate

# OR manually yeh migration file banao:
# HealthCheck_app/migrations/0002_fix_foreign_keys.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('HealthCheck_app', '0001_initial'),  # Adjust based on your last migration
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthchecksession',
            name='initiated_by',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.CASCADE,
                related_name='hc_sessions', 
                to='auth.user'
            ),
        ),
    ]