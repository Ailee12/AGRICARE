# Django Import Error: `execute_from_command_line`

## Error

While starting the Django development server:

```bash
python manage.py runserver
```

the following error occurred:

```text
ImportError: cannot import name 'execute_from_command_line' from 'django.core.management'
```

This was followed by:

```text
ImportError: Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?
```

## Initial Investigation

* Verified that Django was installed:

```bash
pip install django
```

Output showed Django was already installed.

* Checked Django import path:

```bash
python -c "import django; print(django.__file__)"
```

Initially returned:

```text
None
```

which indicated that Python was not loading Django correctly.

* Further inspection revealed that the Django installation inside the virtual environment was corrupted. The package metadata was incomplete and some required files were missing, causing import failures.

## Root Cause

The project's virtual environment (`venv`) became corrupted, resulting in:

* Incomplete Django package installation.
* Missing package metadata.
* Import failures for Django dependencies.
* Inconsistent package resolution within the virtual environment.

## Resolution

The issue was resolved by deleting the corrupted virtual environment and creating a fresh one.

### Steps Taken

```bash
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Verification

After recreating the virtual environment:

```bash
python manage.py runserver
```

Output:

```text
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
```

The application started successfully and all Django system checks passed.

## Lesson Learned

When Django reports import errors despite being installed, and package metadata appears inconsistent, recreating the virtual environment can be faster and more reliable than attempting to repair individual packages.
