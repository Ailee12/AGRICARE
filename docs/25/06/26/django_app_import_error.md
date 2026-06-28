# Django App Import Error: Cannot Import App Configuration

## Error

While creating migrations:

```bash
python manage.py makemigrations --settings=config.settings.local
```

the following error occurred:

```text
django.core.exceptions.ImproperlyConfigured:
Cannot import 'farmers'. Check that 'apps.farmers.apps.FarmersConfig.name' is correct.
```

## Cause

The project follows a modular structure where Django applications are stored inside an `apps` package:

```text
AGRICARE/
├── apps/
│   ├── farmers/
│   ├── users/
│   └── ...
├── config/
└── manage.py
```

However, the app configuration referenced the application as:

```python
name = "farmers"
```

Django attempted to import a top-level package named `farmers`, which does not exist because the actual application resides inside the `apps` package.

## Root Cause

A mismatch existed between the app's physical location and its configured Python import path.

Incorrect configuration:

```python
# apps/farmers/apps.py
class FarmersConfig(AppConfig):
    name = "farmers"
```

Since the application is located inside the `apps` package, Django could not resolve the import path and raised an `ImproperlyConfigured` exception.

## Resolution

Updated the app configuration to use the full Python module path:

```python
# apps/farmers/apps.py
class FarmersConfig(AppConfig):
    name = "apps.farmers"
```

Also ensured that `INSTALLED_APPS` references the application correctly:

```python
INSTALLED_APPS = [
    "apps.farmers",
]
```

or

```python
INSTALLED_APPS = [
    "apps.farmers.apps.FarmersConfig",
]
```

## Verification

After updating the application path:

```bash
python manage.py makemigrations --settings=config.settings.local
```

Django successfully discovered the application and proceeded without the import error.

## Lesson Learned

When using a dedicated `apps/` directory to organize Django applications, always reference applications using their full Python import path (e.g., `apps.farmers`) rather than only the app name (`farmers`). This ensures Django can correctly locate and load the application configuration.
