from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from short_url import decode_url, encode_url

from recipes.models import Recipe


@api_view(['GET'])
def get_short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    short_code = encode_url(pk)
    full_url = request.build_absolute_uri(reverse('redirect_short_link', kwargs={'short_code': short_code}))
    return Response({'short-link': full_url})


def redirect_short_link(request, short_code):
    try:
        recipe_id = decode_url(short_code)
        return redirect(f'http://{request.get_host()}/recipes/{recipe_id}/')
    except ValueError:
        return redirect('/recipes/')
