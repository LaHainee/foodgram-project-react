from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (CustomUser, Favorite, Follow, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from .paginators import CustomPaginator
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (AddFavouriteRecipeSerializer, CreateRecipeSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          ShowFollowersSerializer, TagSerializer,
                          UserSerializer, ShoppingListRecipeSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    permission_classes = (AdminOrAuthorOrReadOnly, )
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action not in ['list', 'retrieve']:
            return CreateRecipeSerializer
        return ListRecipeSerializer

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        serializer_context.update({'request': self.request})
        return serializer_context


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


@api_view()
@permission_classes([IsAuthenticated])
def show_followers(request):
    user_obj = CustomUser.objects.filter(following__user=request.user)
    paginator = PageNumberPagination()
    paginator.page_size = 15
    result_page = paginator.paginate_queryset(user_obj, request)
    serializer = ShowFollowersSerializer(
        result_page, many=True, context={'current_user': request.user})
    return paginator.get_paginated_response(serializer.data)


class FollowViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        user = request.user
        data = {
            'user': user.id,
            'author': user_id
        }
        serializer = UserSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        follow = get_object_or_404(Follow, user=user, author__id=user_id)
        follow.delete()
        return Response('Удалено',
                        status=status.HTTP_204_NO_CONTENT)


class FavouriteViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id
        }
        serializer = AddFavouriteRecipeSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        favorite_obj = get_object_or_404(
            Favorite,
            user=user,
            recipe__id=recipe_id
        )
        if not favorite_obj:
            return Response(
                'Рецепт не был в избранном',
                status=status.HTTP_400_BAD_REQUEST)
        favorite_obj.delete()
        return Response(
            'Удалено', status=status.HTTP_204_NO_CONTENT)


class ShoppingListViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id
        }
        serializer = ShoppingListRecipeSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        shopping_list_obj = get_object_or_404(
            ShoppingList,
            user=user,
            recipe__id=recipe_id
        )
        if not shopping_list_obj:
            return Response(
                'Рецепт не был в списке покупок',
                status=status.HTTP_400_BAD_REQUEST)
        shopping_list_obj.delete()
        return Response(
            'Удалено', status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        shopping_cart = user.shopping_list.all()
        buying_list = {}
        for record in shopping_cart:
            recipe = record.recipe
            ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amount = ingredient.amount
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in buying_list:
                    buying_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    buying_list[name]['amount'] = (buying_list[name]['amount']
                                                   + amount)

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["measurement_unit"]} \n')
        wishlist.append('\n')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
