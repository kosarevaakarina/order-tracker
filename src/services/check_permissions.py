from config.logger import logger
from exceptions import PermissionDeniedException


def check_permissions_users(current_user, user_id=None, superuser_only=False):
    if superuser_only and not current_user.is_superuser:
        logger.error("FORBIDDEN: Insufficient permissions for user ID=%s", current_user.id)
        raise PermissionDeniedException()
    if user_id is not None and current_user.id != user_id and not current_user.is_superuser:
        logger.error("FORBIDDEN: Insufficient permissions for user ID=%s to access user ID=%s", current_user.id, user_id)
        raise PermissionDeniedException()