"""
Migración de datos: crea las cuentas de prueba del modo demostración.

Son las mismas cuentas de database/seed_data.sql, pero con la contraseña
cifrada por Django. Solo se crean en MODO_DEMO; con PostgreSQL los datos
iniciales se cargan con seed_data.sql.

Contraseña de las tres cuentas: Unemi2026*
"""
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations

CONTRASENA_DEMO = "Unemi2026*"

CUENTAS_DE_PRUEBA = (
    {
        "username": "admin.guide",
        "email": "admin.guide@unemi.edu.ec",
        "first_name": "Administrador",
        "last_name": "UNEMI Guide",
        "rol": "ADMINISTRADOR",
        "carrera": "",
        "semestre": None,
        "es_nuevo_ingreso": False,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "mperez",
        "email": "mperez@unemi.edu.ec",
        "first_name": "María",
        "last_name": "Pérez",
        "rol": "ESTUDIANTE",
        "carrera": "Ingeniería de Software",
        "semestre": 1,
        "es_nuevo_ingreso": True,
    },
    {
        "username": "jlopez",
        "email": "jlopez@unemi.edu.ec",
        "first_name": "José",
        "last_name": "López",
        "rol": "DOCENTE",
        "carrera": "Ingeniería de Software",
        "semestre": None,
        "es_nuevo_ingreso": False,
    },
)


def crear_cuentas_de_prueba(apps, schema_editor):
    if not settings.MODO_DEMO:
        return

    Usuario = apps.get_model("users", "Usuario")
    contrasena_cifrada = make_password(CONTRASENA_DEMO)
    for datos in CUENTAS_DE_PRUEBA:
        # get_or_create: la migración se puede ejecutar sin duplicar cuentas.
        Usuario.objects.get_or_create(
            email=datos["email"],
            defaults={**datos, "password": contrasena_cifrada},
        )


def eliminar_cuentas_de_prueba(apps, schema_editor):
    Usuario = apps.get_model("users", "Usuario")
    correos = [datos["email"] for datos in CUENTAS_DE_PRUEBA]
    Usuario.objects.filter(email__in=correos).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_carrera_con_opciones"),
    ]

    operations = [
        migrations.RunPython(crear_cuentas_de_prueba, eliminar_cuentas_de_prueba),
    ]
