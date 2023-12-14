# taskvectorapi

## Overview
This RESTful API for a task management system leverages a Vector Retrieval System for efficient search and retrieval. It allows users to manage tasks with features like creation, update, deletion, and a powerful search functionality based on task similarity.

## Features
- CRUD operations for task management.
- Automatic vector representation generation for tasks.
- Search functionality using vector similarity.
- Token-based authentication.
- Pagination for list retrieval.
- Custom permissions for task operations.

## Technology Stack
- Django & Django REST Framework
- Sentence Transformers for Vector Representation
- SQLite

## Setup and Installation

### Prerequisites
- Python 3.10
- pip
- conda (optional)

### Installation Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/tejangupta/taskvectorapi.git
   cd taskvectorapi
   ```
2. **Set up a Virtual Environment** (Optional but recommended)
   ```bash
   conda create -n taskenv python=3.10 -y
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Initial Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. **Create Superuser** (Optional, for admin access)
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the Server**
   ```bash
   python manage.py runserver
   ```
   
## Usage
Access the API endpoints via http://localhost:8000/api/

Endpoints include:
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}/` - Retrieve a specific task
- `PUT /api/tasks/{id}/` - Update a task
- `DELETE /api/tasks/{id}/` - Delete a task
- `GET /api/tasks/search/{query}/` - Search tasks

## Design Decisions and Assumptions
- **Vector Representation**: Used Sentence Transformers for efficient and accurate text embeddings.
- **Authentication**: Token-based for simplicity and effectiveness.
- **Pagination**: Implemented to handle large numbers of tasks efficiently.
- **Permissions**: Custom permissions ensure only owners can modify their tasks.

## Tests
Run unit tests using:
```bash
python manage.py test tasks
```