import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from core.settings.django.base import BLOCK_DURATION, LOGIN_ATTEMPT_LIMIT, REGISTRATION_ATTEMPT_LIMIT
from core.settings.third_parties.redis import Redis
from core.settings.third_parties.redis_templates import RedisKeyTemplates


class RateLimiterMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.limits = {
            "login": LOGIN_ATTEMPT_LIMIT,
            "register": REGISTRATION_ATTEMPT_LIMIT
        }

    @staticmethod
    def _get_key(key_type, identifier):
        return getattr(RedisKeyTemplates, f"format_{key_type}_attempts_key")(identifier)

    @staticmethod
    def _is_blocked(key):
        block_key = RedisKeyTemplates.format_rate_limiter_key(key=key)
        return Redis.exists(block_key)

    @staticmethod
    def _increment_attempts(key):
        attempts = Redis.incr(key)
        Redis.expire(key, BLOCK_DURATION)
        return attempts

    @staticmethod
    def _block(key):
        block_key = RedisKeyTemplates.format_rate_limiter_key(key=key)
        Redis.set(block_key, 1, ex=BLOCK_DURATION)

    def _handle_rate_limiting(self, key_type, identifier):
        key = self._get_key(key_type, identifier)

        if self._is_blocked(key):
            return self._create_error_response()

        attempts = self._increment_attempts(key)
        if attempts > self.limits[key_type]:
            self._block(key)
            return self._create_error_response()

        return None

    @staticmethod
    def _create_error_response():
        message = _("Too many attempts, please try again later.")
        return JsonResponse({"error": message}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'login' in request.path:
            cellphone = json.loads(request.body).get('cellphone')
            password = json.loads(request.body).get('password')
            ip = request.META.get('REMOTE_ADDR')

            if cellphone and password:
                response = self._handle_rate_limiting('login', f'{cellphone}:{password}')
                if response:
                    return response

                response = self._handle_rate_limiting('login', ip)
                if response:
                    return response

        elif 'register' in request.path:
            cellphone = json.loads(request.body).get('cellphone')
            code = json.loads(request.body).get('code')
            ip = request.META.get('REMOTE_ADDR')

            if cellphone and code:
                response = self._handle_rate_limiting('register', f'{ip}:{cellphone}')
                if response:
                    return response

                response = self._handle_rate_limiting('register', cellphone)
                if response:
                    return response

        return None