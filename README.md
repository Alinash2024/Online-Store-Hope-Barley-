# Online Store "Hope & Barley"

An e-commerce Django application featuring a complete online store with product catalog, shopping cart, order processing, user accounts, and REST API with JWT authentication.

## Description

Hope & Barley is a full-featured online store solution built with Django. It includes a responsive web interface for customers and a comprehensive REST API for external integrations. The application supports product browsing with advanced filtering, shopping cart management, order processing, user authentication, and administration tools.

Key features include:
- Product catalog with search, filters, and pagination
- Shopping cart with real-time calculations
- Secure checkout process with email notifications
- User account system with registration and profile management
- Admin panel with analytics and management tools
- REST API with JWT authentication
- GraphQL endpoint at `/graphql/`
- Docker-based deployment with PostgreSQL

## Installation and Running (via Docker)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 1.29+

### Quick Start
Clone the repository
git clone https://github.com/Alinash2024/Online-Store-Hope-Barley-.git
Build and start all services
docker-compose up
Apply database migrations
docker-compose migrate
Create a superuser (optional)
docker-compose createsuperuser
The application will be available at http://localhost:8000
### Environment Configuration
Create a `.env` file in the project root
SECRET_KEY=your-secret-key 
DEBUG=True 
DATABASE_URL=postgresql://user:password@db:5432/db
JWT_SECRET_KEY= your-secret-key
### Stopping the Application
Stop all services
docker-compose down
Stop all services and remove volumes
docker-compose down -v
## JWT and API Examples
### Authentication
The API uses JWT tokens for authentication. First, obtain a token:
curl -X POST http://localhost:8000/api/auth/login/ 
-H "Content-Type: application/json" 
-d '{"username": "your_username", "password": "your_password"}'
Response:
json { "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." }
### Using the Token
Include the access token in the Authorization header for protected endpoints:
curl -X GET http://localhost:8000/api/products/ -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
### Common API Endpoints
#### Products
- `GET /api/products/` - List all products with filtering options
- `GET /api/products/{id}/` - Get product details
- `POST /api/products/{id}/reviews/` - Add a product review
#### Cart
- `GET /api/cart/` - Retrieve current cart contents
- `POST /api/cart/items/` - Add item to cart
- `PUT /api/cart/items/{item_id}/` - Update item quantity
- `DELETE /api/cart/items/{item_id}/` - Remove item from cart
#### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create a new order
- `GET /api/orders/{id}/` - Get order details
####  Authentication
- `POST /api/auth/login/` - Obtain JWT tokens
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/refresh/` - Refresh access token
### API Documentation
Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
## Running Tests and Linters

### Tests
Run the full test suite:
docker-compose exec web python manage.py test
Run tests for a specific app:
docker-compose exec web python manage.py test apps.
### Linters
Run code quality checks:
Run flake8
docker-compose exec web flake8
### Test Coverage
Generate coverage report:
docker-compose exec web coverage run --source='.' manage.py test
## Project Structure

PythonProject/ 
│── config/ # Project configuration 
│ │── init.py # Project configuration
│ │── asgi.py  # ASGI application
│ ├── settings # Settings packages
│ ├── urls.py # Main URL configuration 
│ └── wsgi.py # WSGI application 
│── orders/ # Order processing 
│ │── templates/ # Templates
│ │── init.py # App configuration
│ │── admin.py # Admin configuration
│ │── api_views.py # API views
│ │── apps.py #  App configuration
│ │── cart.py # Cart logic
│ │── models.py # Order models
│ │── serializers.py # User serializers 
│ │── tests.py # User tests
│ │── urls.py # Account URLs 
│ └── views.py # Authentication views
│── payments/ # Payment processing 
│ ├── templates/ # Templates
│ ├── init.py # App configuration
│ ├── admin.py # Admin configuration
│ ├── apps.py # App configuration
│ ├── models.py # Payment models
│ ├── tests.py # Catalog tests
│ ├── urls.py # Catalog URLs 
│ └── views.py # Product views 
├── products/ # Product catalog
│ ├── templates/ # Templates
│ │── init.py #  App configuration
│ │── admin.py # Admin configuration
│ ├── api_views.py #  API views
│ ├── apps.py # App configuration
│ ├── models.py # Product models
│ ├── serializers.py # Product serializers
│ ├── tests.py # Product tests
│ ├── urls.py # Product URLs
│ └── views.py # Product views
├── reviews/ # Product reviews
│ ├── templates/ # Templates
│ ├── init.py # App configuration
│ ├── admin.py # Admin configuration
│ ├── api_views.py # API views
│ ├── apps.py # App configuration
│ ├── forms.py # Review forms
│ ├── models.py # Review models
│ ├── serializers.py # Review serializers
│ ├── tests.py # Review tests
│ ├── urls.py # Review URLs
│ └── views.py # Review views
├── shop_graphql/ # GraphQL API
│ ├── init.py # App configuration
│ ├── admin.py # Admin configuration
│ ├── apps.py # App configuration
│ ├── models.py # GraphQL models
│ ├── shop_schema.py # GraphQL schema
│ ├── tests.py # GraphQL tests
│ └── views.py # GraphQL views
├── templates/ # HTML templates
│ └── admin/  # Admin templates
── users/ # User authentication and profiles 
│ │── templates/ # HTML templates
│ │── init.py # App configuration
│ │── admin.py # Admin configuration
│ ├── api_views.py # API views
│ │── apps.py # App configuration
│ │── forms.py # User forms
│ │── models.py # User, Profile models
│ │── serializers.py # User serializers
│ │── tests.py # User tests
│ │── urls.py # Account URLs
│ └── views.py #  Authentication views
├── .dockerignore/  # Docker ignore file
├── .env.example/ # Environment variables example
├── .gitignore/ #  Git ignore file
├── docker-compose.yml # Docker services configuration 
├── Dockerfile # Web service Docker image 
├── manage.py # Django CLI utility 
├── poetry.lock/ # Poetry lock file
└── pyproject.toml/ #  Project metadata

### Key Directories Explained
- `apps/`: Contains all Django applications, each responsible for a specific domain.
#### Apps Directory (`apps/`)
Contains all Django applications, each responsible for a specific domain:
- `accounts`: User registration, authentication, and profile management
- `catalog`: Product and category management with search functionality
- `cart`: Shopping cart operations and management
- `orders`: Order processing, fulfillment, and tracking
- `api`: REST API endpoints with JWT authentication
- `analytics`: Business intelligence and reporting features
- `payments`: Payment processing and integration with third-party services
- `reviews`: Product reviews and ratings
- `shop_graphql`: GraphQL API for complex queries and mutations
- `users`: User authentication and profile management
#### Configuration (`config/`)
Contains project-wide configuration settings, such as URL routing and database settings.
#### Templates
Contains HTML templates for each app, organized by app name.
