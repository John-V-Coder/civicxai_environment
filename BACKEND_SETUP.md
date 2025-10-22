# Complete Backend Setup Guide - CivicXAI

## Critical Installation Steps Before Running

### Step 1: Create Virtual Environment (Recommended)
```bash
# Navigate to project root
cd civic-xai-environment

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Core Dependencies
```bash
cd civicxai_backend

# Install updated requirements
pip install -r requirements_updated.txt

# If you get any errors, try installing individually:
pip install Django==5.1.6
pip install djangorestframework==3.15.2
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.7.0
pip install python-dotenv==1.0.1
pip install openai==1.35.0
pip install PyJWT==2.8.0
```

### Step 3: Install MeTTa/Hyperon (Special Installation)
```bash
# MeTTa requires special installation
# Option 1: From GitHub (Recommended)
pip install git+https://github.com/singnet/hyperon-experimental.git

# Option 2: If above fails, try:
pip install hyperon

# If still having issues, you might need to build from source:
# git clone https://github.com/singnet/hyperon-experimental.git
# cd hyperon-experimental
# pip install -e .
```

### Step 4: Install uAgents Framework
```bash
# Install uagents and dependencies
pip install uagents cosmpy ecdsa bech32

# Verify installation
python -c "import uagents; print(uagents.__version__)"
```

### Step 5: Create Environment Files
```bash
# Create .env file in civicxai_backend directory
cd civicxai_backend
```

Create `.env` file with:
```env
# Django Settings
SECRET_KEY='django-insecure-0k*ia&3t*gb!u8-=$ndglgl1#p##o&_y2_g=w013lqr3+bw(dr'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (using SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# AI API Keys
ASI_ONE_API_KEY=your_asi_one_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# uAgents Configuration
AI_PROVIDER_AGENT_SEED=ai_explanation_provider_secret_seed
GATEWAY_AGENT_SEED=civic_xai_chat_gateway_secret_seed

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Step 6: Database Setup
```bash
# Remove old database if exists
rm -f db.sqlite3

# Create new migrations
python manage.py makemigrations explainable_ai

# Apply migrations
python manage.py migrate

# If you get an error about AUTH_USER_MODEL:
python manage.py migrate --run-syncdb
```

### Step 7: Create Superuser
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@civicxai.com
# Password: (choose a strong password)
```

### Step 8: Load Sample Data
```bash
# Create management commands directories if they don't exist
mkdir -p explainable_ai/management/commands/

# Run the populate command
python manage.py populate_sample_data
```

### Step 9: Verify MeTTa Files
```bash
# Check if MeTTa policy file exists
ls metta/civic_policies.metta

# If not, ensure the metta directory and file exist
```

### Step 10: Test the Installation
```bash
# Run Django development server
python manage.py runserver

# In another terminal, test the health endpoint
curl http://localhost:8000/api/health/

# Should return: {"status": "healthy", "metta_engine": "operational", ...}
```

## Common Installation Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'hyperon'
**Solution:**
```bash
# Try alternative installation methods
pip install --upgrade pip
pip install metta-lang
# or
pip install hyperon-experimental
```

### Issue 2: ImportError with uagents
**Solution:**
```bash
# Install specific version
pip install uagents==0.14.0
# Ensure all dependencies are installed
pip install cosmpy ecdsa bech32 aiohttp
```

### Issue 3: Database Migration Errors
**Solution:**
```bash
# Complete reset
rm -rf explainable_ai/migrations/
mkdir explainable_ai/migrations/
touch explainable_ai/migrations/__init__.py
rm -f db.sqlite3

# Recreate
python manage.py makemigrations explainable_ai
python manage.py migrate
```

### Issue 4: JWT Authentication Not Working
**Solution:**
```bash
# Ensure all JWT packages are installed
pip install djangorestframework-simplejwt PyJWT
pip install django-cors-headers

# Check settings.py has proper configuration
# Verify SIMPLE_JWT settings are complete
```

### Issue 5: CORS Issues
**Solution:**
Add to settings.py:
```python
CORS_ALLOW_ALL_ORIGINS = True  # For development only
# Or specify specific origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

## Verification Checklist

Run these commands to verify everything is installed correctly:

```bash
# 1. Check Python packages
python -c "import django; print('Django:', django.__VERSION__)"
python -c "import rest_framework; print('DRF: OK')"
python -c "import rest_framework_simplejwt; print('JWT: OK')"
python -c "import corsheaders; print('CORS: OK')"
python -c "import dotenv; print('Dotenv: OK')"
python -c "import openai; print('OpenAI: OK')"

# 2. Check MeTTa (might fail if not properly installed)
python -c "from hyperon import MeTTa; print('MeTTa: OK')"

# 3. Check uAgents
python -c "from uagents import Agent; print('uAgents: OK')"

# 4. Test Django setup
python manage.py check

# 5. Test API endpoints
python manage.py runserver
# Then visit: http://localhost:8000/api/
```

## Quick Start After Installation

```bash
# 1. Start Django server
cd civicxai_backend
python manage.py runserver

# 2. In new terminal, start uAgents AI Provider (optional)
cd uagents_ai_provider
python main.py

# 3. In another terminal, start uAgents Gateway (optional)
cd uagents_gateway/gateway
python main.py
```

## What Each Package Does

| Package | Purpose |
|---------|---------|
| `djangorestframework-simplejwt` | JWT authentication |
| `django-cors-headers` | Handle CORS for frontend |
| `python-dotenv` | Load environment variables |
| `openai` | AI explanations via GPT |
| `hyperon/metta` | Policy rule engine |
| `uagents` | Decentralized agent framework |
| `django-filter` | API filtering |
| `drf-yasg` | API documentation |
| `Pillow` | Image handling for profiles |
| `celery` | Async task processing |
| `redis` | Caching and message broker |

## Security Notes

Before deploying to production:
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG=False`
3. Configure proper `ALLOWED_HOSTS`
4. Use PostgreSQL instead of SQLite
5. Set up proper CORS origins (not allow all)
6. Use environment variables for all sensitive data
7. Enable HTTPS

## Next Steps

Once everything is installed and verified:
1. Access admin panel: http://localhost:8000/admin/
2. Test API authentication: http://localhost:8000/api/auth/login/
3. Check dashboard metrics: http://localhost:8000/api/dashboard/
4. Start building the frontend to consume these APIs

---

**Important:** If MeTTa/Hyperon installation fails, the system will still work but without the symbolic AI policy engine. You can comment out the MeTTa imports in `metta_engine.py` temporarily.
