from cProfile import Profile
from rest_framework import serializers
from .models import Contact, SpamPhoneNumber, UserMapContact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class UserMapContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMapContact
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class SpamPhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamPhoneNumber
        fields = '__all__'

