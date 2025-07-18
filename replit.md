# Overview

This is a Streamlit-based Student Assignment Submission and Management System. The application allows students to submit assignments online while enabling professors (administrators) to monitor submission status. The system features role-based access with two user types: students and administrators (professors). Data is stored in SQLite database and files are saved to local server folders.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit for web interface
- **Design Pattern**: Single-page application with role-based views
- **User Interface**: Simple, intuitive forms and dashboards
- **Authentication**: Session-based login system with role differentiation

## Backend Architecture
- **Language**: Python
- **Framework**: Streamlit (handles both frontend and backend)
- **Architecture Pattern**: Monolithic application structure
- **File Organization**: Single main application file (app.py) with modular functions

## Data Storage
- **Database**: SQLite for lightweight, file-based data storage
- **File Storage**: Local server directory (storage/) for assignment files
- **Data Persistence**: All data stored locally on server filesystem

# Key Components

## Database Schema
The system uses three main tables:

1. **students table**
   - `student_id` (TEXT, Primary Key): Student ID (e.g., '20251111')
   - `password` (TEXT): Hashed password for security
   - `name` (TEXT): Student name
   - `email` (TEXT): Email address

2. **professors table**
   - `admin_id` (TEXT, Primary Key): Administrator ID (e.g., 'admin1')
   - `password` (TEXT): Hashed password for security
   - `name` (TEXT): Professor name

3. **submissions table**
   - `submission_id` (INTEGER, Primary Key, Autoincrement): Unique submission ID
   - `student_id` (TEXT): Foreign key to students table

## User Roles
- **Students**: Can submit assignments and view their submission history
- **Administrators/Professors**: Can view all submissions and manage the system

## File Management
- Assignment files stored in `storage/` directory
- Local filesystem storage for simplicity and direct access

# Data Flow

1. **User Authentication**: Users login with credentials stored in SQLite database
2. **Role-based Routing**: System redirects to appropriate interface based on user role
3. **Assignment Submission**: Students upload files to storage directory with metadata saved to database
4. **Data Retrieval**: Professors query database to view submission status and access files
5. **Session Management**: Streamlit handles user sessions and state management

# External Dependencies

## Python Packages
- **Streamlit**: Web application framework
- **SQLite3**: Database connectivity (built into Python)
- **Hashlib**: Password hashing for security
- **OS/File System**: Local file operations for assignment storage

## Database Dependencies
- **SQLite**: Lightweight, serverless database engine
- **No external database server required**

# Deployment Strategy

## Local Development
- Single Python file execution with Streamlit
- SQLite database file creation on first run
- Local storage directory initialization

## File Structure
```
project/
├── app.py                 # Main Streamlit application
├── database.db           # SQLite database file
└── storage/              # Assignment file storage directory
```

## Deployment Considerations
- **Scalability**: Current architecture suitable for small to medium class sizes
- **Security**: Password hashing implemented, but consider additional security measures for production
- **Backup**: Regular backup of database.db and storage/ directory recommended
- **Access Control**: File-based storage requires proper server-level access controls

## Future Enhancements
- Consider database migration to PostgreSQL for larger deployments
- Implement file upload size limits and type restrictions
- Add email notification system for submission confirmations
- Implement audit logging for administrative actions