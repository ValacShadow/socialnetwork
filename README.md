# Social Network API

This project is a social network API built with Django and Django Rest Framework.

## Installation

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:
   git clone https://github.com/yourusername/socialnetwork.git
   cd socialnetwork
   python manage.py runserver

Build and run the Docker containers:
docker-compose up --build

Apply database migrations:
docker-compose exec web python manage.py migrate

Create a superuser:
docker-compose exec web python manage.py createsuperuser

API Endpoints
POST /api/signup/: User signup
POST /api/login/: User login
GET /api/search/?q=keyword: Search users by email or name
POST /api/friend-request/: Send friend request
PUT /api/friend-request/accept/<id>/: Accept friend request
PUT /api/friend-request/reject/<id>/: Reject friend request
GET /api/friends/: List friends
GET /api/friend-requests/pending/: List pending friend requests
