# Data Sources - Admin Only Access

## 🔒 Security Implementation

The Data Sources feature is now **fully secured** and only accessible to administrators.

---

## ✅ What Was Secured

### 1. **Frontend Protection**
- ✅ Route wrapped with `ProtectedRoute` requiring admin role
- ✅ Sidebar link hidden for non-admin users
- ✅ Beautiful "Access Denied" page for unauthorized access attempts
- ✅ Role check: `user?.role === 'admin'`

### 2. **Backend Protection**
- ✅ API endpoints secured with `IsAdminOnly` permission
- ✅ All CRUD operations require admin authentication
- ✅ Custom permission checks both authentication AND admin role
- ✅ Django admin panel also protected (superuser only)

### 3. **User Roles**
Only these users can access Data Sources:
- ✅ **Admin** (`role: 'admin'`)
- ✅ **Superuser** (`is_superuser: true`)

---

## 🚀 How to Create Admin User

### Option 1: Using the Quick Script (Easiest)

```bash
cd civicxai_backend
python create_admin.py
```

Follow the prompts to create an admin user.

### Option 2: Django Management Command

```bash
cd civicxai_backend
python manage.py createsuperuser
```

Then update the user's role to admin via Django admin or database.

### Option 3: Manual Database Update

```python
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

# Get your user
user = User.objects.get(username='your_username')

# Update to admin
user.role = 'admin'
user.is_staff = True
user.is_superuser = True
user.save()

print(f"✅ {user.username} is now an admin!")
```

---

## 🔐 Access Control Matrix

| User Type | Can View Data Sources | Can Add Sources | Can Edit Sources | Can Delete Sources |
|-----------|----------------------|-----------------|------------------|-------------------|
| **Guest** (not logged in) | ❌ No | ❌ No | ❌ No | ❌ No |
| **Citizen** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Contributor** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Analyst** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 📍 Where to Access (Admin Only)

### Frontend
1. Login as admin user
2. Navigate to sidebar → **AI Features** section
3. Click **Data Sources** (🗄️ database icon)
4. Add, edit, or delete sources

### Django Admin
1. Go to: `http://localhost:8000/admin`
2. Login with admin credentials
3. Click **Data sources**
4. Full CRUD operations available

---

## 🛡️ Security Features

### Frontend
```javascript
// Route protection in App.jsx
<Route path="data-sources" element={
  <ProtectedRoute requireAdmin={true}>
    <DataSources />
  </ProtectedRoute>
} />

// Sidebar visibility check
if (item.href === '/data-sources' && user?.role !== 'admin') {
  return null; // Hide from non-admins
}
```

### Backend
```python
# datasource_views.py
class DataSourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOnly]  # Enforced on all endpoints
    
# permissions.py
class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )
```

---

## 🚨 What Happens on Unauthorized Access

### Non-Admin User Tries to Access
1. **Via URL:** Redirected to "Access Denied" page with message
2. **Via API:** Receives `403 Forbidden` response
3. **Sidebar:** Link not visible at all

### Guest User (Not Logged In)
1. **Via URL:** Redirected to login page
2. **Via API:** Receives `401 Unauthorized` response
3. **Sidebar:** Link not visible

---

## 🔧 Testing Security

### Test as Different User Roles

1. **Create test users:**
```bash
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

# Create citizen user
User.objects.create_user(
    username='citizen_test',
    password='test123',
    role='citizen'
)

# Create admin user
User.objects.create_user(
    username='admin_test',
    password='admin123',
    role='admin',
    is_staff=True,
    is_superuser=True
)
```

2. **Test access:**
- Login as `citizen_test` → Data Sources link should NOT appear
- Try accessing `/data-sources` → Should see "Access Denied"
- Login as `admin_test` → Data Sources link SHOULD appear
- Access `/data-sources` → Should work perfectly

---

## 📊 API Endpoints (All Admin Only)

```javascript
// All these require admin authentication
GET    /api/data-sources/              // List all sources
POST   /api/data-sources/              // Create new source
GET    /api/data-sources/{id}/         // Get specific source
PATCH  /api/data-sources/{id}/         // Update source
DELETE /api/data-sources/{id}/         // Delete source

// Additional endpoints
GET    /api/data-sources/active/       // Get active sources
GET    /api/data-sources/stats/        // Get statistics
GET    /api/data-sources/search_sources/ // Search sources
```

---

## ✅ Verification Checklist

Before deploying, verify:

- [ ] Admin user created and can login
- [ ] Admin user can see "Data Sources" in sidebar
- [ ] Admin user can access `/data-sources` page
- [ ] Admin user can add/edit/delete sources
- [ ] Non-admin user CANNOT see "Data Sources" in sidebar
- [ ] Non-admin user gets "Access Denied" when accessing `/data-sources`
- [ ] API returns 403 for non-admin users
- [ ] Guest users are redirected to login

---

## 🎯 Data Integrity Protected

With admin-only access:
- ✅ Only authorized personnel can add sources
- ✅ Prevents data tampering by regular users
- ✅ Ensures AI references are trustworthy
- ✅ Maintains knowledge base quality
- ✅ Audit trail via Django admin logs

---

## 🔄 Next Steps

1. **Run migrations:**
   ```bash
   cd civicxai_backend
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create admin user:**
   ```bash
   python create_admin.py
   ```

3. **Test access control:**
   - Login as admin → Access granted ✅
   - Login as citizen → Access denied ❌
   - Not logged in → Redirect to login ↩️

4. **Add your first sources** (as admin)

---

## 📝 Notes

- The AI chat can still **USE** sources when responding to users
- Only **managing** (add/edit/delete) sources is admin-only
- Sources are automatically referenced in chat responses
- Usage statistics track which sources are most helpful

---

**Security Status:** 🔒 **FULLY SECURED** - Admin Only Access Enforced
