from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination as PNPagination
)

from foodgram.constants import PAGE_SIZE_QUERY_PARAM, PAGE_QUERY_PARAM


class PageNumberPagination(PNPagination):
    page_query_param = PAGE_QUERY_PARAM
    page_size_query_param = PAGE_SIZE_QUERY_PARAM


class RecipesLimitPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
    offset_query_param = None
