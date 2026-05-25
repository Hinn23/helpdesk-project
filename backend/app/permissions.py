ROLES_HIERARCHY = {
    "guest": 0,
    "user": 1,
    "support": 2,
    "moderator": 3,
    "junior_admin": 4,
    "manager": 4,
    "admin": 5,
}

STAFF_ROLES = ("admin", "junior_admin", "manager", "moderator", "support")


def role_at_least(user, min_role: str) -> bool:
    return ROLES_HIERARCHY.get(user.role, 0) >= ROLES_HIERARCHY.get(min_role, 0)


def can_manage_tickets(user) -> bool:
    return user.role in STAFF_ROLES or True


def can_manage_users(user) -> bool:
    return user.role in ("admin", "junior_admin")


def can_manage_tags(user) -> bool:
    return user.role in ("admin", "manager")


def can_view_moderation(user) -> bool:
    return user.role in ("admin", "junior_admin", "manager", "moderator")


def can_delete_ticket(user, ticket) -> bool:
    return user.role in ("admin", "manager") or ticket.author_id == user.id


def can_bulk_actions(user) -> bool:
    return user.role == "admin"


def can_edit_closed(user) -> bool:
    return user.role in ("admin", "junior_admin", "moderator")


def can_warn(user) -> bool:
    return user.role in ("admin", "junior_admin")


def is_staff(user) -> bool:
    return user.role in STAFF_ROLES
