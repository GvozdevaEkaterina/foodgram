from rest_framework.pagination import PageNumberPagination as PNPagination


class PageNumberPagination(PNPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
