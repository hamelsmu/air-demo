# Database

Minimal Air app using SQLModel with PostgreSQL.

Shows async database operations with HTMX for dynamic updates.

## Setup

```bash
# Install PostgreSQL if not already installed
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database
createdb air_demo

# Install dependencies
pip install sqlmodel asyncpg

# Run
fastapi dev database/main.py
```
