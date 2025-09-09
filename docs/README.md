# CampusHub 360 Documentation App

A comprehensive documentation system for CampusHub 360 APIs and tutorials, built with Django and styled like W3Schools for easy understanding.

## Features

### 📚 Tutorials
- Step-by-step guides with detailed instructions
- Code examples in multiple programming languages
- Difficulty levels (Beginner, Intermediate, Advanced)
- Estimated reading time
- Prerequisites and tags
- View tracking

### 🔌 API Documentation
- Complete API endpoint documentation
- Request/response schemas
- Code examples for different languages
- Authentication requirements
- Rate limiting information
- Status codes and error handling

### 🏷️ Categories
- Organized content by categories
- Color-coded and icon-based navigation
- Easy browsing and filtering

### 🔍 Search
- Global search across all content
- Filter by category, difficulty, and method
- Real-time search results

### ❓ FAQ
- Frequently asked questions
- Categorized answers
- Easy-to-navigate accordion interface

## Models

### Category
- Organizes tutorials and API endpoints
- Includes icons, colors, and descriptions
- Ordering support

### Tutorial
- Main tutorial content with markdown support
- Difficulty levels and time estimates
- Author attribution and view tracking
- Featured tutorials support

### APIEndpoint
- Complete API documentation
- Request/response schemas (JSON)
- Authentication and rate limiting info
- Method-specific documentation

### CodeExample
- Code snippets for tutorials and APIs
- Multiple language support
- Syntax highlighting with Prism.js

### Step
- Step-by-step tutorial instructions
- Ordered progression
- Markdown content support

### FAQ
- Question and answer pairs
- Category organization
- Published/unpublished status

## URLs

- `/docs/` - Home page with featured content
- `/docs/tutorials/` - List all tutorials
- `/docs/tutorials/<slug>/` - Tutorial detail page
- `/docs/apis/` - List all API endpoints
- `/docs/apis/<id>/` - API endpoint detail page
- `/docs/categories/` - List all categories
- `/docs/categories/<slug>/` - Category detail page
- `/docs/search/` - Search functionality
- `/docs/faq/` - Frequently asked questions
- `/docs/api/json/` - JSON API for frontend integration

## Admin Interface

The app includes a comprehensive Django admin interface for managing:
- Categories with color and icon customization
- Tutorials with rich text editing
- API endpoints with JSON schema editing
- Code examples with syntax highlighting
- Steps and FAQ management

## Sample Data

Run the management command to populate sample data:

```bash
python manage.py populate_sample_data
```

This creates:
- 5 categories (Authentication, Students, Faculty, Academics, Attendance)
- 3 tutorials with steps and code examples
- 3 API endpoints with documentation
- 5 FAQ entries

## Frontend Integration

The documentation provides a JSON API endpoint for frontend integration:

```javascript
// Get all tutorials
fetch('/docs/api/json/?type=tutorials')
  .then(response => response.json())
  .then(data => console.log(data.tutorials));

// Get all API endpoints
fetch('/docs/api/json/?type=apis')
  .then(response => response.json())
  .then(data => console.log(data.apis));

// Get all categories
fetch('/docs/api/json/?type=categories')
  .then(response => response.json())
  .then(data => console.log(data.categories));
```

## Styling

The documentation uses a W3Schools-inspired design with:
- Clean, modern interface
- Responsive Bootstrap 5 layout
- Font Awesome icons
- Syntax highlighting with Prism.js
- Interactive elements and smooth scrolling
- Color-coded difficulty levels and HTTP methods

## Customization

### Adding New Categories
1. Go to Django Admin > Documentation > Categories
2. Add new category with icon, color, and description
3. Set order for display sequence

### Creating Tutorials
1. Go to Django Admin > Documentation > Tutorials
2. Create tutorial with markdown content
3. Add steps and code examples
4. Set difficulty and estimated time

### Documenting APIs
1. Go to Django Admin > Documentation > API Endpoints
2. Add endpoint with method and description
3. Define request/response schemas
4. Add code examples for different languages

## Development

### Adding New Features
1. Extend models in `models.py`
2. Create views in `views.py`
3. Add URL patterns in `urls.py`
4. Create templates in `templates/docs/`
5. Update admin interface in `admin.py`

### Testing
```bash
python manage.py test docs
```

### Migrations
```bash
python manage.py makemigrations docs
python manage.py migrate
```

## Deployment

The documentation app is ready for production deployment with:
- Static file serving
- Database optimization
- Caching support
- Security best practices

## Support

For questions or issues with the documentation system, please contact the development team or create an issue in the project repository.
