from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from link_shortner.views import get_short_link, redirect_short_link
from recipes.views import (
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('s/<str:short_code>/', redirect_short_link, name='redirect_short_link'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/recipes/<int:pk>/get-link/', get_short_link, name='get_short_link'),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )