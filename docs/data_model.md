# Data Model Documentation

## Overview

The Helpdesk Lite system uses 4 main entities: User, Ticket, Comment, and Category.

## Entity Relationship Diagram

```
User (1) ---< (N) Ticket (assignee)
Ticket (1) ---< (N) Comment
Category (1) ---< (N) Ticket
```

## User

| Field    | Type   | Constraints          |
|----------|--------|----------------------|
| id       | Integer| PK, auto-increment   |
| name     | String | NOT NULL              |
| email    | String | UNIQUE, NOT NULL, indexed |
| password | String | NOT NULL (hashed)    |
| role     | String | Default: "user"      |

**Valid roles:** `admin`, `user`, `guest`

## Ticket

| Field       | Type     | Constraints          |
|-------------|----------|----------------------|
| id          | Integer  | PK, auto-increment   |
| title       | String   | NOT NULL, indexed     |
| description | Text     | Default: ""           |
| status      | String   | Default: "new"        |
| priority    | String   | Default: "medium"     |
| deadline    | DateTime | Nullable             |
| assignee_id | Integer  | FK -> users.id, nullable |
| category_id | Integer  | FK -> categories.id, nullable |
| created_at  | DateTime | Auto-set             |
| updated_at  | DateTime | Auto-updated          |

**Valid statuses:** `new`, `in_progress`, `done`, `cancelled`
**Valid priorities:** `low`, `medium`, `high`

## Comment

| Field      | Type     | Constraints          |
|------------|----------|----------------------|
| id         | Integer  | PK, auto-increment   |
| ticket_id  | Integer  | FK -> tickets.id, NOT NULL, indexed |
| author_name| String   | NOT NULL             |
| text       | Text     | NOT NULL             |
| created_at | DateTime | Auto-set             |

## Category

| Field       | Type   | Constraints          |
|-------------|--------|----------------------|
| id          | Integer| PK, auto-increment   |
| name        | String | UNIQUE, NOT NULL, indexed |
| description | Text   | Default: ""           |

## Database

- **Engine:** SQLite (file: `helpdesk.db`)
- **ORM:** SQLAlchemy 2.0 with Declarative Base
- **Migrations:** Manual (Alembic optional)

## Seed Data

The `seed.py` script populates:
- 3 users (admin, alice, bob)
- 4 categories (Bug, Feature, Support, Documentation)
- 12 tickets with various statuses and priorities
- 12 comments spread across tickets
