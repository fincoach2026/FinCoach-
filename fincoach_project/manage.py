#!/usr/bin/env python
"""
manage.py — the command you run to control the project.

Beginner note: this is what you type things like this into:
    python manage.py runserver       -> starts the local dev server
    python manage.py makemigrations  -> prepares database changes
    python manage.py migrate         -> applies database changes
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincoach_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed by running:\n"
            "    pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
