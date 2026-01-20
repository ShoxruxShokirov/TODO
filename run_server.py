#!/usr/bin/env python
"""
Django server startup script with automatic migrations.
This script ensures migrations are run before starting the server.
"""
import os
import sys
import subprocess

def run_command(command, description, critical=True):
    """Run a Django management command."""
    print(f"\n{'=' * 50}")
    print(f"{description}")
    print(f"{'=' * 50}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=critical,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            if critical:
                print(f"ERROR: {description} failed with exit code {result.returncode}")
                return False
            else:
                print(f"WARNING: {description} failed, but continuing...")
                return True
    except subprocess.CalledProcessError as e:
        if critical:
            print(f"ERROR: {description} failed: {e}")
            return False
        else:
            print(f"WARNING: {description} failed: {e}, but continuing...")
            return True
    except Exception as e:
        if critical:
            print(f"ERROR: {description} failed with exception: {e}")
            return False
        else:
            print(f"WARNING: {description} failed: {e}, but continuing...")
            return True

if __name__ == '__main__':
    print("=" * 50)
    print("Django TODO App - Server Startup")
    print("=" * 50)
    
    # Step 1: Run migrations (CRITICAL - must succeed)
    if not run_command(
        'python manage.py migrate --noinput',
        'Running database migrations',
        critical=True
    ):
        print("\nFATAL ERROR: Migrations failed. Exiting...")
        sys.exit(1)
    
    # Step 2: Start Gunicorn
    print("\n" + "=" * 50)
    print("Starting Gunicorn server...")
    print("=" * 50)
    # Get PORT from environment (Render sets this automatically)
    port = os.environ.get('PORT', '8000')
    print(f"Binding to port: {port}")
    
    # Start Gunicorn - use the simplest reliable method
    cmd = [
        sys.executable, '-m', 'gunicorn',
        'todo_project.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-'
    ]
    print(f"Executing: {' '.join(cmd)}")
    os.execv(sys.executable, cmd)

