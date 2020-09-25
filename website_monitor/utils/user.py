import logging

from django.contrib.auth import get_user_model

from api.models import UserProfile

logger = logging.getLogger(__name__)


def _create_user_profile_and_set_scopes(user, token_scopes):
    scopes = ','.join(token_scopes)
    try:
        user_profile = UserProfile.objects.get(user=user)
        user_profile.scopes = scopes
        user_profile.save()
        logger.debug('Updated user scopes')
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=user, scopes=scopes)
        user_profile.save()
        logger.debug('Created UserProfile and updated user scopes')

    return user_profile


def _create_user_if_does_not_exist(username, email):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        logger.debug(f'Found User: {user}')
    except User.DoesNotExist:
        user = User.objects.create_user(username, email)
        logger.debug(f'Created User: {user}')

    return user


def jwt_get_username_from_payload_handler(payload):
    logger.debug(f'JWT Token payload: {payload}')
    username = payload.get('sub').replace('|', '.')
    email = payload.get('http://website-monitor.liopetas.com/email')
    token_scopes = payload.get('scope').split()
    user = _create_user_if_does_not_exist(username, email)
    _create_user_profile_and_set_scopes(user, token_scopes)
    return user
