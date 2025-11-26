from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import MenuItem, MenuCategory, PriceChange
from .serializers import MenuItemSerializer, MenuCategorySerializer, PriceChangeSerializer

MANAGER_LEVEL = 4  # same as Role level for Manager

class CreateMenuItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only allow managers or higher (owner level is higher)
        user = request.user
        if not user.role or user.role.level < MANAGER_LEVEL:
            return Response({"error": "Only managers or owners can add menu items"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MenuItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleMenuItemAvailability(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Only allow managers or higher
        user = request.user
        if not user.role or user.role.level < MANAGER_LEVEL:
            return Response({"error": "Only managers or owners can toggle menu items"}, status=status.HTTP_403_FORBIDDEN)

        try:
            item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Toggle available flag or accept explicit value
        explicit = request.data.get('available')
        if explicit is not None:
            item.available = bool(explicit)
        else:
            item.available = not item.available

        item.save()
        serializer = MenuItemSerializer(item, context={'request': request})
        return Response(serializer.data)

class GetAllCategories(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return a list of all menu categories.
        Each item contains:
          - id
          - name
        """
        categories = MenuCategory.objects.all().order_by('name')
        serializer = MenuCategorySerializer(categories, many=True)
        return Response({"categories": serializer.data})

class GetAllMenuItems(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Fetch all menu items, but allow optional filtering:
        - ?category=<id>
        - ?available=true / false
        Both filters may be combined.
        """

        items = MenuItem.objects.select_related('category').all()

        # Handle ?category=2
        category_id = request.GET.get("category")
        if category_id:
            items = items.filter(category_id=category_id)

        # Handle ?available=true or ?available=false
        available_param = request.GET.get("available")
        if available_param is not None:
            if available_param.lower() == "true":
                items = items.filter(available=True)
            elif available_param.lower() == "false":
                items = items.filter(available=False)

        # Prepare results
        results = []
        for item in items:
            # Generate absolute image URL if available
            image_url = None
            if item.image:
                try:
                    image_url = request.build_absolute_uri(item.image.url)
                except:
                    image_url = item.image.url

            results.append({
                "id": item.id,
                "name": item.name,
                "category_name": item.category.name if item.category else None,
                "category_id": item.category.id if item.category else None,
                "description": item.description,
                "price": str(item.price),
                "available": item.available,
                "image_url": image_url,
                "cooking_options": item.cooking_options,
            })

        return Response({"menu_items": results})

class ChangeMenuItemPrice(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """
        Change price of menu item with id=pk.
        Body: { "new_price": "12.99", "reason": "special price" }
        Only manager or owner (role.level >= MANAGER_LEVEL) may do this.
        """

        user = request.user

        # Permission check: must have a role and be manager or above
        if not user.role or user.role.level < MANAGER_LEVEL:
            return Response({"error": "Only managers or owners can change the prices of menu items."}, status=status.HTTP_403_FORBIDDEN)

        try:
            item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PriceChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_price = serializer.validated_data['new_price']
        reason = serializer.validated_data.get('reason', '')

        # Record old price then update
        old_price = item.price
        item.price = new_price
        item.save()

        # Create audit record
        PriceChange.objects.create(
            menu_item=item,
            changed_by=user,
            old_price=old_price,
            new_price=new_price,
            reason=reason
        )

        return Response({
            "message": "Price updated",
            "menu_item": {
                "id": item.id,
                "name": item.name,
                "old_price": str(old_price),
                "new_price": str(new_price)
            }
        }, status=status.HTTP_200_OK)