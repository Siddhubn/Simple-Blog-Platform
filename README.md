# Simple Blog Platform

This is a simple blog platform built using Flask with HTML and CSS for the frontend. It allows users to create, view, and delete blog posts.
---
## Features
- Create new blog posts
- View all posts on the homepage
- View individual posts
- Delete posts
- Responsive dark-themed UI
---
## File Structure
```
.
├── templates/
│   ├── create.html (Form to create a new post)
│   ├── index.html (Homepage displaying all posts)
│   ├── post.html (View individual posts)
├── venv/ (virtual environment)
├── app.py (Flask backend for handling routes)
├── database.db (SQLite database for storing posts)
├── README.md (This file)
```
---
## Templates Overview
### create.html
- Contains a form for creating new posts with fields for title and content.
- Uses a stylish dark theme with responsive design.
- Buttons for submitting the post and canceling.

### index.html
- Displays a list of all blog posts.
- Each post is a clickable link to view full content.
- Includes a delete button for removing posts.
- Provides a button to create a new post.

### post.html
- Displays a single blog post with its title and content.
- Includes a button to return to the homepage.
---
## Technologies Used
- Flask (Backend framework)
- HTML & CSS (Frontend)
- SQLite (Database for storing posts)
---
## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/Siddhubn/Simple-Blog-Platform/
   cd Simple-Blog-Platform
   ```
2. Activate virtual environment:
   ```sh
   venv/Scripts/activate  # On Windows use: venv\Scripts\activate
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Open the browser and go to:
   ```
   http://127.0.0.1:5000/
   ```
---
## Usage
- Click "Create New Post" to add a new blog post.
- Click on a post title to view its content.
- Click "Delete" to remove a post.
---
## Future Enhancements
- User authentication system
- Edit post functionality
- Improved database management
- Rich text editor for creating posts
---
## Author:
This project's author is [Siddharth B N](https://github.com/Siddhubn).
