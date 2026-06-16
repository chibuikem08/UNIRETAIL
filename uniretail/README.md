# UniRetail — University Online Retail Management System

A Django-based online marketplace for university campuses where vendors can showcase their shops and students/staff can order and pay before pickup.

---

## 👥 User Roles

| Role | Description |
|------|-------------|
| **Student** | Browse shops, add to cart, place and pay for orders |
| **Staff** | Same as student |
| **Vendor** | Manage shop, list products, fulfill orders (requires admin approval) |
| **Admin** | Full platform access, approve vendors, view all orders |

---

## 🚀 Tech Stack

- **Backend:** Django 4.2 + Python 3.x
- **Database:** PostgreSQL
- **Frontend:** Bootstrap 5 + vanilla HTML/CSS/JS
- **Payments:** Paystack (with demo/simulation mode)
- **Static files:** WhiteNoise

---

## ⚙️ Local Setup

```bash
# 1. Clone and enter project
cd uniretail

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key

# 5. Create PostgreSQL database
# In psql: CREATE DATABASE uniretail_db;

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser
# Then in Django admin, set role to ADMIN

# 8. Run development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## 🔑 Environment Variables (.env)

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=uniretail_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Optional — leave blank for demo/simulation mode
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_SECRET_KEY=sk_test_...
```

---

## 📦 Project Structure

```
uniretail/
├── accounts/       Custom user model, auth (register/login/profile)
├── shops/          Shops and products (browse + vendor management)
├── orders/         Cart, checkout, order tracking
├── payments/       Paystack integration + payment history
├── dashboard/      Vendor dashboard + Admin dashboard
├── templates/      All HTML templates
├── static/         CSS, JS, images
└── uniretail/      Django config (settings, urls)
```

---

## 🧪 Test Accounts (after setup)

Create these manually via `/accounts/register/`:
- **Admin:** Create via `createsuperuser`, set role=ADMIN in Django admin
- **Vendor:** Register with Vendor role, approve via admin dashboard
- **Student:** Register with Student role, start shopping immediately

---

## 💳 Paystack Integration

- Without keys: uses **Demo Mode** (simulates successful payment)
- With keys: get them free at https://dashboard.paystack.com/#/settings/developer
- Add `PAYSTACK_PUBLIC_KEY` and `PAYSTACK_SECRET_KEY` to `.env`

---

## 📋 Order Flow

```
Student adds to cart
      ↓
   Checkout
      ↓
  Pay Now (Paystack or Demo)
      ↓
 Order = PENDING
      ↓
Vendor confirms → CONFIRMED
      ↓
Vendor marks ready → READY FOR PICKUP
      ↓
Student collects → COMPLETED
```
