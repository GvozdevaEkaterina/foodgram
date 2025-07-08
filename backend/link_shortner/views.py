from django.shortcuts import get_object_or_404, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from short_url import decode_url, encode_url

from foodgram.constants import SHORT_LINK_BASE_URL
from recipes.models import Recipe


@api_view(['GET'])
def get_short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    short_code = encode_url(pk)
    short_url = f'{SHORT_LINK_BASE_URL}/s/{short_code}'
    return Response({'short-link': short_url})


def redirect_short_link(request, short_code):
    try:
        recipe_id = decode_url(short_code)
        return redirect(f'{SHORT_LINK_BASE_URL}/recipes/{recipe_id}/')
    except ValueError:
        return redirect('/recipes/')
