"""
Quick script to create an admin user
Run: python create_admin.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicxai_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    """Create an admin user"""
    
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@civicxai.com): ").strip() or "admin@civicxai.com"
    password = input("Enter admin password (default: admin123): ").strip() or "admin123"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"\n❌ User '{username}' already exists!")
        update = input("Update to admin role? (y/n): ").strip().lower()
        if update == 'y':
            user = User.objects.get(username=username)
            user.role = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"✅ Updated '{username}' to admin role!")
        return
    
    # Create new admin user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"\n✅ Admin user created successfully!")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"\nYou can now login with these credentials.")

if __name__ == "__main__":
    print("=" * 50)
    print("CivicXAI - Create Admin User")
    print("=" * 50)
    create_admin()
