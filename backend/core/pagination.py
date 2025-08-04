from rest_framework.pagination import LimitOffsetPagination


class RecipesLimitPagination(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'
    offset_query_param = 'recipes_offset'
