
# 🛍️ T-Shirt eCommerce Website

A fully functional T-Shirt eCommerce website built using Django Users can browse, filter, and purchase t-shirts, while admins can manage products and orders.

---

## 🚀 Features

- 🧾 User Registration & Login (for Authentication)
- 🛒 Shopping Cart & Checkout
- 👕 Product Listing with Images and Descriptions
- 🔍 Product Search & Filters
- 📦 Order Placement & Management
- 💳 Stripe Payment Gateway Integration
- 📧 Email Verification & Order Confirmation
- 🧑‍💼 Admin Panel for Managing Users, Products, and Orders

---

## 🔧 Technologies Used

- **Backend:** Django,
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** SQLite / PostgreSQL (configurable)
- **Payments:** Stripe API
- **Auth:** django-authentication

## 📁 Project Structure

```
ecom/

├── account/                # User auth and profile
        |---login
        |---registration
        |---reset-password
        |---change-password
├── products/                # Product CRUD 
├── orders/                  # Order placement and history
├── ecom/                    # Core project settings
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # Uploaded images
└── manage.py
```

---

## 🛠️ Setup Instructions

1. **Clone the Repository**

git clone https://github.com/indrajee2/Django-Ecommerce.git
cd tshirt-ecommerce

2. **Create and Activate Virtual Environment**

python -m venv ecomenv
.\ecomenv\Scripts\activate  # On Windows


3. **Install Dependencies**

pip install -r requirements.txt


4. **Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create Superuser**

```bash
python manage.py createsuperuser
```

6. **Start Development Server**

```bash
python manage.py runserver
```

7. Visit [http://127.0.0.1:8000](http://localhost:8000)

---

## ✅ To-Do / Improvements

- Add product reviews and ratings
- Implement user wishlist
- Add real-time order tracking
- Dockerize for production

---

## 📸 Screenshots

> _(Add screenshots of homepage, product page, cart, and checkout here)_

---

## 📬 Contact

- 👤 Indra Jeet
- 📧 [indrajee323@gmail.com]
- 🌐 [(https://www.linkedin.com/in/indrajeet-sharma-9a3348232/)]

---

## 📄 License

This project is licensed under the MIT License -."# Django-Ecommerce" 
