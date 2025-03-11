from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from django.db.models import Count
from django.db import IntegrityError
from django.utils.timezone import now

from .permissions import IsEmployee, IsRestaurantOwner

from .models import Restaurant, Menu, Vote
from .serializers import RestaurantSerializer, MenuSerializer, VoteSerializer, RegisterSerializer


# get application version
def get_build_version(request):
    return request.headers.get('X-Build-Version', '2.0')


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Only the restaurant owners can create restaurants
        if self.action == 'create':
            return [IsRestaurantOwner()]
        # All authenticated users can view restaurants
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Assign the current user as the restaurant owner
        serializer.save(owner=self.request.user)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Only restaurant owners can create menus
        if self.action == 'create':
            return [IsRestaurantOwner()]
        # All authenticated users can view menus
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Ensure the menu is added only to a restaurant owned by the user
        restaurant = serializer.validated_data['restaurant']

        if restaurant.owner != self.request.user:
            raise PermissionDenied("You can only add a menu to your own restaurant.")

        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError('You can only add one menu per day.')

    def get_serializer_context(self):
        # pass the version to serializer context
        context = super().get_serializer_context()
        context['build_version'] = get_build_version(self.request)
        return context

    @action(detail=False, methods=['get'], url_path='current-day')
    def get_current_day_menu(self, request):
        today = now().date()
        menus = Menu.objects.filter(date=today)

        if menus.exists():
            return Response(MenuSerializer(menus, many=True).data)
        else:
            return Response({"message": "No menus for today."}, status=404)

    @action(detail=False, methods=['get'], url_path='most-voted-today')
    def get_most_voted_today(self, request):
        today = now().date()
        votes_today = Vote.objects.filter(date=today)
        menu_votes = votes_today.values('menu').annotate(vote_count=Count('id')).order_by('-vote_count')

        if menu_votes.exists():
            # The most voted menu
            most_voted_menu_id = menu_votes[0]['menu']
            most_voted_menu = Menu.objects.get(id=most_voted_menu_id)
            return Response(MenuSerializer(most_voted_menu).data)
        else:
            return Response({"message": "No votes today."}, status=404)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allows only employees to vote, but all authenticated users can view votes
        if self.action == 'create':
            return [IsEmployee()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Ensures that the employee can vote only once per day.
        user = self.request.user

        try:
            serializer.save(employee=user)
        except IntegrityError:
            raise ValidationError("You have already voted today.")


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "username": user.username},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
