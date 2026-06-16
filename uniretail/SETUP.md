# ============================================================
#  UniRetail — Setup Guide
#  Run these commands ONE BY ONE in your terminal
# ============================================================

# ── Step 1: Create & activate a virtual environment ──────────
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# ── Step 2: Install dependencies ─────────────────────────────
pip install -r requirements.txt

# ── Step 3: Set up your environment variables ─────────────────
# Copy the example file and edit it with your DB credentials
cp .env.example .env
# Now open .env in a text editor and fill in your PostgreSQL details

# ── Step 4: Create the PostgreSQL database ────────────────────
# Open psql and run:
#   CREATE DATABASE uniretail_db;
# Or use pgAdmin to create a database named: uniretail_db

# ── Step 5: Run migrations ────────────────────────────────────
python manage.py makemigrations accounts
python manage.py makemigrations
python manage.py migrate

# ── Step 6: Create a superuser (admin) ───────────────────────
python manage.py createsuperuser
# When prompted, fill in:
#   Username: admin
#   Email: admin@university.edu
#   Password: (your choice)
# Then in Django admin, manually set the role to ADMIN

# ── Step 7: Run the development server ───────────────────────
python manage.py runserver

# Visit: http://127.0.0.1:8000
# Admin panel: http://127.0.0.1:8000/admin/

# ============================================================
