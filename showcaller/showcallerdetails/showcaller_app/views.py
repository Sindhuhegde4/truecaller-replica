from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import status,permissions
from .models import Contact, UserMapContact, Profile, SpamPhoneNumber
from .serializers import ContactSerializer, UserMapContactSerializer, ProfileSerializer, SpamPhoneNumberSerializer



class SignUp(APIView):
    def post(self, request):
        name = request.data.get("name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email", None)
        password = request.data.get("password")

        if not (name and phone_number and password):
            return Response(
                {"Error": "Name, phone number, and password are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the provided phone number is already registered
        if Profile.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"Error": "This phone number is already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the provided phone number is marked as spam
        if SpamPhoneNumber.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"Error": "This phone number is marked as spam."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new user
        user = User.objects.create_user(username=name, password=password, email=email)

        # Create a new profile
        profile = Profile.objects.create(user=user, phone_number=phone_number, email=email)

        return Response(
            {"Message": "User registered successfully."},
            status=status.HTTP_201_CREATED
        )

    def get(self, request):
        return Response(
            {"Error": "GET method not allowed. Please use POST method to register."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

@permission_classes((AllowAny,))
class LoginHere(APIView):
    def post(self, request):
        # Check if request data is provided
        if not request.data:
            return Response(
                {"Error": "Please provide username and password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract username and password from request data
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Check if username and password are provided
        if not username or not password:
            return Response(
                {"Error": "Both username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        # Check if authentication is successful
        if user is not None:
            # Generate token for authenticated user
            token, created = Token.objects.get_or_create(user=user)
            
            # Additional information about the user
            user_info = {
                "username": user.username,
                "email": user.email,
                # Add more fields as needed
            }
            
            return Response(
                {
                    "Message": "Login successful",
                    "Token": token.key,
                    "User": user_info
                },
                status=status.HTTP_200_OK
            )
        else:
            # Authentication failed
            return Response(
                {"Error": "Invalid username or password. Please check your credentials and try again."},
                status=status.HTTP_401_UNAUTHORIZED
            )

class MarkAsSpam(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        
        # Check if phone_number is empty or None
        if not phone_number:
            return Response(
                {"Error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if phone_number is a valid numeric value
        try:
            phone_number = int(phone_number)
        except ValueError:
            return Response(
                {"Error": "Invalid phone number format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update contact and profile if they exist
        contact_updated = Contact.objects.filter(phone_number=phone_number).update(spam=True)
        profile_updated = Profile.objects.filter(phone_number=phone_number).update(spam=True)
        
        if contact_updated or profile_updated:
            return Response(
                {"Message": "Contact marked as spam successfully."},
                status=status.HTTP_200_OK
            )
        else:
            # If the contact was not found, create a new entry in the SpamPhoneNumber model
            spam = SpamPhoneNumber.objects.create(phone_number=phone_number)
            return Response(
                {"Message": "New phone number marked as spam."},
                status=status.HTTP_200_OK
            )
class SearchName(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get("name")  

        if name is None:
            return Response(
                {"Error": "Name is required!!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_start = Profile.objects.filter(user__username__startswith=name)
        profile_contain = Profile.objects.filter(user__username__contains=name).exclude(user__username__startswith=name)
        contact_start = Contact.objects.filter(name__startswith=name)
        contact_contain = Contact.objects.filter(name__contains=name).exclude(name__startswith=name)

        response = []

        for contact in profile_start:
            user = contact.user
            response.append(
                {
                    "name": user.username,
                    "phone_number": contact.phone_number,
                    "email": contact.email,
                    "spam": contact.spam,
                }
            )

        for contact in profile_contain:
            user = contact.user
            response.append(
                {
                    "name": user.username,
                    "phone_number": contact.phone_number,
                    "email": contact.email,
                    "spam": contact.spam,
                }
            )

        for contact in contact_start:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "email": contact.email,
                    "spam": contact.spam,
                }
            )

        for contact in contact_contain:
            response.append(
                {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "email": contact.email,
                    "spam": contact.spam,
                }
            )

        serializer = ContactSerializer(response, many=True)
        return Response(serializer.data)

    def get(self, request):
        return self.post(request)

class SearchPhoneNumber(APIView):
    def get(self, request):
        phone_number = request.query_params.get("phone_number")  
        if phone_number is None:
            return Response(
                {"Error": "Phone number required!!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Using .first() to get the first (and only) instance from the queryset
        profile = Profile.objects.filter(phone_number=phone_number).first()

        if profile:
            user = profile.user
            return Response(
                {
                    "name": user.username,
                    "phone_number": profile.phone_number,
                    "spam": profile.spam,
                    "email": profile.email
                }
            )
        else:
            contact = Contact.objects.filter(phone_number=phone_number)
            serializer = ContactSerializer(contact, many=True)
            return Response(serializer.data)


class ListSpamNumbers(APIView):
    def get(self, request):
        spam_numbers = SpamPhoneNumber.objects.all()
        serializer = SpamPhoneNumberSerializer(spam_numbers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
