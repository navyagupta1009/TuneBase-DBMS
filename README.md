# TuneBase — Music Library Management System

TuneBase is a DBMS project for organizing music-library information. It uses MySQL for data storage, Flask for backend processing, and HTML/CSS for the user interface.

## Features

- CRUD operations: Create, Read, Update, and Delete
- Dashboard for viewing database information
- Search and table browsing
- Foreign-key dropdowns for related records
- SQL schema, sample data, and example queries

## Technology Stack

- Python
- Flask
- MySQL
- XAMPP and phpMyAdmin
- HTML and CSS
- mysql-connector-python

## Database Tables

The database contains eight tables:

1. `Users`
2. `Artists`
3. `Albums`
4. `Songs`
5. `Playlists`
6. `Playlist_Songs`
7. `Likes`
8. `Listening_History`

## Project Structure

```text
TuneBase-DBMS/
├── app.py
├── schema.sql
├── seed.sql
├── queries.sql
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── docs/
│   ├── ER_Diagram.png
│   └── project-report.pdf
└── .gitignore
```

Adjust the diagram and report filenames to match the files actually included in the repository.

## Prerequisites

Install Python 3 and XAMPP.

## Setup Instructions

### 1. Start MySQL

1. Open the XAMPP Control Panel.
2. Start MySQL.
3. Open phpMyAdmin at `http://localhost/phpmyadmin`.

Start Apache too if needed to access phpMyAdmin through XAMPP.

### 2. Create and populate the database

In phpMyAdmin, import `schema.sql` first, followed by `seed.sql`.

If the database and tables already exist, avoid importing the schema repeatedly into a database containing records you want to preserve.

### 3. Install dependencies

Open a terminal in the project directory and run:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the database connection

The current application is configured for a local MySQL server using these default settings:

- Host: `127.0.0.1`
- Port: `3306`
- Username: `root`
- Password: blank

Make sure these match your MySQL configuration. If necessary, update the connection settings in `app.py`. Never commit real passwords or other private credentials to GitHub.

### 5. Run the application

From the project directory, run:

```bash
python app.py
```

Open the following address in your browser:

`http://127.0.0.1:5000/`

This address works on the computer running the Flask application. To run TuneBase on another computer, download the repository, install the prerequisites, import the database, and start Flask there.

## SQL Files

- `schema.sql` — creates the database tables and constraints.
- `seed.sql` — inserts sample records.
- `queries.sql` — contains example SQL queries.

## Database Design

The project includes a relational schema with primary keys, foreign keys, and other integrity constraints. The database is designed to meet Third Normal Form (3NF); the final report should explain 1NF, 2NF, and 3NF based on the actual schema.

The complete ER diagram should show all attributes, primary and foreign keys, cardinalities, and participation constraints.

## Testing

The dashboard opened successfully during local testing. CRUD operations passed for Artists, Albums, and Songs. The other five tables were checked, but their individual CRUD outcomes and the remaining constraint tests should be documented after verification.

## Security

- Do not upload passwords, API keys, or private credentials.
- Do not upload `.env` files containing secrets.
- Do not upload virtual environments such as `venv/` or `.venv/`.
- The Flask development server is intended for local testing and demonstration, not production deployment.

## Authors

Add the project team members' names here.
