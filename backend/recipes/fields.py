from rest_framework import serializers

from .models import Ingredient, Tag


class IngredientField(serializers.RelatedField):
    """
    Кастомное поле сериализатора для работы с ингредиентами.
    Преобразует данные между форматами:
    - В API: {id, name, measurement_unit, amount}
    - В БД: {ingredient_id, amount}
    """
    def get_queryset(self):
        return Ingredient.objects.all()

    def to_representation(self, value):
        return {
            'id': value.ingredient.id,
            'name': value.ingredient.name,
            'measurement_unit': value.ingredient.measurement_unit,
            'amount': value.amount
        }

    def to_internal_value(self, data):
        try:
            return {
                'ingredient_id': data['id'],
                'amount': data['amount']
            }
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError('Ингредиент не найден')
        except KeyError:
            raise serializers.ValidationError(
                'Необходимы "id" и "amount" ингредиента'
            )


class TagField(serializers.RelatedField):
    """
    Кастомное поле сериализатора для работы с тегами.
    Преобразует данные между форматами:
    - В API: {id, name, slug}
    - В БД: Возвращает Tag по его ID
    """
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(f'Тег с ID {data} не существует')
