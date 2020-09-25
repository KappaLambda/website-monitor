import logging

from rest_framework import permissions

from api.models import UserProfile

logger = logging.getLogger(__name__)


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class TokenHasScope(permissions.BasePermission):

    def has_permission(self, request, view):
        user_profile = UserProfile.objects.get(user=request.user)
        user_scopes = user_profile.scopes.split(',')

        if not hasattr(view, 'required_scopes'):
            logger.error(f'Attribute "required_scopes" missing in {view}')
            return False

        for scope in view.required_scopes:
            if scope not in user_scopes:
                return False

        return True
