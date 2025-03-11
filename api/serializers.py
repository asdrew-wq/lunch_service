from rest_framework import serializers
from django.contrib.auth.models import User, Group
from rest_framework.exceptions import ValidationError
import json

from .models import Restaurant, Menu, Vote


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description']


class MenuSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), source='restaurant', write_only=True
    )
    content = serializers.JSONField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        build_version = self.context.get('build_version', '2.0')

        # Parse content to dict
        content = representation['content']
        if isinstance(content, str):
            representation['content'] = json.loads(content)

        # Moving content to items (for version 1)
        if build_version.startswith('1.'):
            representation['items'] = representation.pop('content')

        return representation

    def to_internal_value(self, data):
        build_version = self.context.get('build_version', '2.0')
        mutable_data = data.copy()
        if build_version.startswith('1.') and 'items' in mutable_data:
            items = mutable_data.pop('items')
            if isinstance(items, dict):
                mutable_data['content'] = json.dumps(items)
            else:
                mutable_data['content'] = items
        return super().to_internal_value(mutable_data)

    def validate(self, data):
        restaurant = data.get('restaurant')
        date = data.get('date', self.instance.date if self.instance else None)
        if restaurant and date:
            if Menu.objects.filter(restaurant=restaurant, date=date).exists():
                raise serializers.ValidationError(
                    {"detail": "You can only add one menu per day."}
                )
        return data

    def validate_content(self, value):
        # Ensure that value is a valid JSON or dict
        if isinstance(value, str):
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Value must be valid JSON.")
        return value

    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'restaurant_id', 'content', 'date']


class VoteSerializer(serializers.ModelSerializer):
    menu = MenuSerializer(read_only=True)  # Full information for GET requests
    menu_id = serializers.PrimaryKeyRelatedField(
        queryset=Menu.objects.all(), source='menu',
        write_only=True
    )  # Only the id for POST requests

    class Meta:
        model = Vote
        fields = ['id', 'employee', 'menu', 'menu_id', 'date']
        read_only_fields = ['employee']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    is_employee = serializers.BooleanField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email is already taken.")
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()

        # Assign role based on is_employee
        if validated_data["is_employee"]:
            # Assign employee role
            employee_group = Group.objects.get(name="Employee")
            user.groups.add(employee_group)
        else:
            # Assign restaurant owner role
            owner_group = Group.objects.get(name="RestaurantOwner")
            user.groups.add(owner_group)

        return user
