Complete Backend Setup Guide – CivicX
Critical Installation Steps Before Running
Step 1: Create Virtual Environment (Recommended)
cd civic-x-environment
python -m venv venv

# Activate
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

Step 2: Install Core Dependencies
cd civicx_backend
pip install -r requirements_updated.txt

# If any fail, install individually
pip install Django==5.1.6
pip install djangorestframework==3.15.2
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.7.0
pip install python-dotenv==1.0.1
pip install PyJWT==2.8.0

Step 3: Install MeTTa/Hyperon (Special Installation)
# Option 1 (recommended)
pip install git+https://github.com/singnet/hyperon-experimental.git

# Option 2 (simpler)
pip install hyperon

# Option 3 (from source)
git clone https://github.com/singnet/hyperon-experimental.git
cd hyperon-experimental
pip install -e .

Step 4: Install uAgents Framework
pip install uagents cosmpy ecdsa bech32
python -c "import uagents; print(uagents.__version__)"

Step 5: Create Environment Files
cd civicx_backend


Create .env file:

# Django Settings
SECRET_KEY='django-insecure-0k*ia&3t*gb!u8-=$ndglgl1#p##o&_y2_g=w013lqr3+bw(dr'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# API Keys
ASI_ONE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# uAgents Configuration
PROVIDER_AGENT_SEED=explanation_provider_secret_seed
GATEWAY_AGENT_SEED=civic_gateway_secret_seed

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

Step 6: Database Setup
rm -f db.sqlite3
python manage.py makemigrations knowledge_core
python manage.py migrate
python manage.py migrate --run-syncdb

Step 7: Create Superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@civicx.com
# Password: (your choice)

Step 8: Load Sample Data
mkdir -p knowledge_core/management/commands/
python manage.py populate_sample_data

Step 9: Verify MeTTa Files
ls metta/civic_policies.metta

Step 10: Test the Installation
python manage.py runserver
curl http://localhost:8000/api/health/
# Expected: {"status": "healthy", "metta_engine": "operational", ...}

Common Installation Issues

1. ModuleNotFoundError: No module named 'hyperon'

pip install --upgrade pip
pip install metta-lang
pip install hyperon-experimental


2. ImportError with uAgents

pip install uagents==0.14.0
pip install cosmpy ecdsa bech32 aiohttp


3. Database Migration Errors

rm -rf knowledge_core/migrations/
mkdir knowledge_core/migrations/
touch knowledge_core/migrations/__init__.py
rm -f db.sqlite3
python manage.py makemigrations knowledge_core
python manage.py migrate


4. JWT Authentication Issues

pip install djangorestframework-simplejwt PyJWT
pip install django-cors-headers


5. CORS Problems

CORS_ALLOW_ALL_ORIGINS = True  # for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True

Verification Checklist
python -c "import django; print('Django:', django.__VERSION__)"
python -c "import rest_framework; print('DRF: OK')"
python -c "import rest_framework_simplejwt; print('JWT: OK')"
python -c "import corsheaders; print('CORS: OK')"
python -c "import dotenv; print('Dotenv: OK')"
python -c "from hyperon import MeTTa; print('MeTTa: OK')"
python -c "from uagents import Agent; print('uAgents: OK')"
python manage.py check
python manage.py runserver

Quick Start After Installation
cd civicx_backend
python manage.py runserver

# Start Provider Agent (optional)
cd uagents_provider
python main.py

# Start Gateway (optional)
cd uagents_gateway/gateway
python main.py

Package Overview
Package	Purpose
djangorestframework-simplejwt	Authentication
django-cors-headers	Frontend communication
python-dotenv	Environment variables
hyperon/metta	Knowledge and reasoning engine
uagents	Decentralized communication
django-filter	Query filtering
drf-yasg	API documentation
Pillow	Image handling
celery	Background task processing
redis	Caching and message broker
Security Notes

Before production deployment:

Change SECRET_KEY

Set DEBUG=False

Configure proper ALLOWED_HOSTS

Use PostgreSQL instead of SQLite

Restrict CORS origins

Store secrets in .env

Enable HTTPS

Next Steps

Access the admin panel at http://localhost:8000/admin/

Test authentication at http://localhost:8000/api/auth/login/

Check dashboard metrics at http://localhost:8000/api/dashboard/

Connect the frontend to the backend APIs

If MeTTa or Hyperon fails to install, you can comment out their imports in metta_engine.py; the backend will continue running without symbolic reasoning.