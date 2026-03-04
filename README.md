# Privacy-First Video Survey Backend

A Dockerized FastAPI backend application for creating and managing privacy-focused video surveys.

This project demonstrates REST API design, database modeling, Docker containerization, and backend architecture principles.

---

# 🏗 Architecture Overview

The system consists of two main services:

1. Backend (FastAPI)
2. PostgreSQL Database

Both services run inside Docker containers and are orchestrated using Docker Compose.

The backend communicates with PostgreSQL using the internal Docker hostname `db` instead of localhost.

### System Flow

Client (Browser / Postman)
        ↓
FastAPI Backend (Docker Container)
        ↓
PostgreSQL Database (Docker Container)

The backend handles:
- Survey creation
- Question management
- Survey publishing
- Submission handling
- Media storage
- Basic GeoIP lookup

---

# 🧰 Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL 15
- Docker
- Docker Compose
- Uvicorn ASGI Server

---

# 🚀 Setup Instructions (Docker - Recommended)

## 1. Clone Repository

```bash
git clone <your_repo_url>
cd privacy-video-survey-backend