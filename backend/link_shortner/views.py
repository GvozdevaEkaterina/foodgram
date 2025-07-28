"""Приложение для сокращения ссылок."""

from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from short_url import decode_url, encode_url


@api_view(['GET'])
def get_short_link(request, pk):
    """Генерирует короткую ссылку на рецепт."""

    short_code = encode_url(pk)
    full_url = request.build_absolute_uri(
        reverse('redirect_short_link', kwargs={'short_code': short_code})
    )
    return Response({'short-link': full_url})


def redirect_short_link(request, short_code):
    """Переадресовывает с короткой ссылки на полную страницу рецепта."""

    try:
        recipe_id = decode_url(short_code)
        return redirect(f'https://{request.get_host()}/recipes/{recipe_id}/')
    except ValueError:
        return redirect('/recipes/')
