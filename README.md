# Django TODO App - Premium Edition

A professional, production-ready TODO application built with Django, featuring modern UI/UX design and advanced functionality.

## ✨ Features

### Core Functionality
- **User Authentication** - Secure registration and login system
- **Task Management (CRUD)** - Create, Read, Update, Delete tasks
- **Task Filtering** - Filter by All / Active / Completed status
- **Search Functionality** - Search tasks by title and description
- **Task Sorting** - Sort by date, priority, or due date

### Advanced Features
- **Priority System** - Low, Medium, High priority levels with color coding
- **Due Dates** - Set deadlines for tasks with overdue indicators
- **Task Descriptions** - Add detailed descriptions to tasks
- **Modern UI/UX** - Premium gradient design with smooth animations
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Class-Based Views** - Professional Django architecture
- **Database Indexing** - Optimized queries for better performance

## 🛠 Tech Stack

- **Backend**: Python 3.8+, Django 5.0+
- **Database**: SQLite (development), PostgreSQL ready (production)
- **Frontend**: Bootstrap 5.3, Font Awesome 6.4
- **Architecture**: Class-Based Views, Mixins, Model Forms

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/django-todo-app
cd django-todo-app
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser (optional, for admin panel):**
```bash
python manage.py createsuperuser
```

6. **Run the development server:**
```bash
python manage.py runserver
```

7. **Open your browser and navigate to:**
```
http://127.0.0.1:8000
```

## 🚀 Usage

1. **Registration/Login**
   - Click "Register here" to create a new account
   - Or login with existing credentials

2. **Creating Tasks**
   - Enter task title in the form
   - Optionally add description, priority, and due date
   - Click "Add Task" button

3. **Managing Tasks**
   - **Complete/Undo**: Click the Complete/Undo button
   - **Edit**: Click Edit to modify task details
   - **Delete**: Click Delete to remove a task
   - **Filter**: Use All/Active/Completed buttons to filter
   - **Search**: Use the search bar to find tasks
   - **Sort**: Use the sort dropdown to organize tasks

4. **Priority Levels**
   - **Low** (Green): Non-urgent tasks
   - **Medium** (Yellow): Normal priority
   - **High** (Red): Urgent tasks

## 📁 Project Structure

```
todo_project/
├── todo_project/          # Main project settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI config
│   └── asgi.py            # ASGI config
│
├── tasks/                 # Tasks application
│   ├── models.py          # Task model with priority, due_date, etc.
│   ├── views.py           # Class-based views (ListView, CreateView, etc.)
│   ├── urls.py            # Task URLs
│   ├── forms.py           # Task and Register forms
│   ├── admin.py           # Admin configuration
│   ├── templates/
│   │   └── tasks/
│   │       ├── task_list.html      # Main task list view
│   │       └── task_form.html      # Create/Edit task form
│   └── migrations/        # Database migrations
│
├── templates/             # Global templates
│   └── registration/
│       ├── login.html     # Login page
│       └── register.html  # Registration page
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🏗 Architecture Highlights

### Class-Based Views
- `TaskListView` - Displays filtered and sorted task list
- `TaskCreateView` - Handles task creation
- `TaskUpdateView` - Handles task editing
- `TaskDeleteView` - Handles task deletion

### Models
- **Task Model** with fields:
  - title, description, completed
  - priority (low/medium/high)
  - due_date, created_at, updated_at
  - user (ForeignKey to User)
  - Helper methods: `is_overdue()`, `get_priority_color()`

### Database Optimization
- Indexes on frequently queried fields
- Efficient queryset filtering
- Proper foreign key relationships

## 🎨 Design Features

- **Modern Gradient Backgrounds** - Beautiful purple gradient theme
- **Smooth Animations** - Slide-up and fade-in effects
- **Color-Coded Priorities** - Visual priority indicators
- **Responsive Cards** - Clean, modern card design
- **Font Awesome Icons** - Professional iconography
- **Hover Effects** - Interactive UI elements

## 🔒 Security Features

- CSRF protection
- User authentication required for all task operations
- User isolation (users can only see/edit their own tasks)
- Secure password handling
- SQL injection protection (Django ORM)

## 📝 Development Notes

### Running Migrations
After making model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser
```bash
python manage.py createsuperuser
```

### Accessing Admin Panel
```
http://127.0.0.1:8000/admin/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

**Shoxrux**

---

⭐ If you find this project helpful, please give it a star!
