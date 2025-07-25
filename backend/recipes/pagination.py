from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class CustomPageNumberPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'


class RecipesLimitPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
    offset_query_param = 'recipes_offset'
