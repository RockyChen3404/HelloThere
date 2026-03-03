from models.order import OrderStatus
from models.user import UserRole

# Define allowed transitions per role
ALLOWED_TRANSITIONS = {
    UserRole.merchant: {
        OrderStatus.pending: OrderStatus.accepted,
        OrderStatus.accepted: OrderStatus.preparing,
        OrderStatus.preparing: OrderStatus.ready,
    },
    UserRole.rider: {
        OrderStatus.ready: OrderStatus.delivering,
        OrderStatus.delivering: OrderStatus.delivered,
    },
    UserRole.customer: {
        OrderStatus.delivered: OrderStatus.completed,
        # customer can cancel before accepted
        OrderStatus.pending: OrderStatus.cancelled,
    },
}


def can_transition(current_status: OrderStatus, new_status: OrderStatus, role: UserRole) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(role, {})
    return allowed.get(current_status) == new_status


def get_next_statuses(current_status: OrderStatus, role: UserRole) -> list:
    allowed = ALLOWED_TRANSITIONS.get(role, {})
    next_s = allowed.get(current_status)
    result = [next_s] if next_s else []
    # Merchant can also cancel pending orders
    if role == UserRole.merchant and current_status in (
        OrderStatus.pending, OrderStatus.accepted, OrderStatus.preparing
    ):
        result.append(OrderStatus.cancelled)
    return result
