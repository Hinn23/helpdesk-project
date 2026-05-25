# Helpdesk Lite API Documentation

## Base URL
`http://localhost:8000`

## Health

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "app": "practice_project",
  "version": "0.1.0"
}
```

## Authentication

### POST /auth/register
Register a new user.

**Body:** `{ "name": "string", "email": "string", "password": "string", "role": "user" }`

**Response:** `{ "access_token": "string", "token_type": "bearer", "user_id": 1, "role": "user" }`

### POST /auth/login
Login with email and password.

**Body:** `{ "email": "string", "password": "string" }`

**Response:** `{ "access_token": "string", "token_type": "bearer", "user_id": 1, "role": "user" }`

### GET /auth/me
Get current user info. Requires Bearer token.

**Headers:** `Authorization: Bearer <token>`

**Response:** `{ "id": 1, "name": "string", "email": "string", "role": "user" }`

## Users

All user endpoints require admin role (`Authorization: Bearer <token>`).

### GET /users/
List all users.

### GET /users/{id}
Get user by ID.

### POST /users/
Create user.

### PUT /users/{id}
Update user.

### DELETE /users/{id}
Delete user.

## Tickets

Authentication is optional (Bearer token or X-User-Role header).

### GET /tickets/
List tickets with pagination, filtering, sorting.

**Parameters:**
- `skip` (int, default 0) - Offset
- `limit` (int, default 10, max 100) - Page size
- `status` (str, optional) - Filter by status
- `priority` (str, optional) - Filter by priority
- `search` (str, optional) - Search in title/description
- `category_id` (int, optional) - Filter by category
- `assignee_id` (int, optional) - Filter by assignee
- `sort` (str, default "created_at") - Sort field
- `order` (str, default "desc") - Sort order (asc/desc)

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 10,
  "pages": 10
}
```

### GET /tickets/{id}
Get ticket by ID.

### POST /tickets/
Create ticket.

**Body:** `{ "title": "string", "description": "string", "status": "new", "priority": "medium", "deadline": "ISO datetime", "assignee_id": 1, "category_id": 1 }`

### PUT /tickets/{id}
Update ticket.

### DELETE /tickets/{id}
Delete ticket.

## Comments

### GET /tickets/{ticket_id}/comments/
List comments for a ticket.

### POST /tickets/{ticket_id}/comments/
Add comment to ticket.

**Body:** `{ "author_name": "string", "text": "string" }`

### DELETE /tickets/{ticket_id}/comments/{comment_id}
Delete comment.

## Categories

### GET /categories/
List categories.

### GET /categories/{id}
Get category.

### POST /categories/
Create category.

### PUT /categories/{id}
Update category.

### DELETE /categories/{id}
Delete category.

## Error Responses

- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error (Pydantic)
- `500` - Internal Server Error

## Status Values
- `new`, `on_moderation`, `in_progress`, `done`, `cancelled`

## Priority Values
- `low`, `medium`, `high`

## Role Values
- `admin`, `user`, `guest`
