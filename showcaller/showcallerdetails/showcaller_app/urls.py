from django.urls import path
from .views import ListSpamNumbers, SignUp, LoginHere, MarkAsSpam, SearchName, SearchPhoneNumber


urlpatterns=[
	path('signup/', SignUp.as_view()),
	path('login/', LoginHere.as_view()),
	path('mark_as_spam/', MarkAsSpam.as_view()),
	path('search_name/', SearchName.as_view()),
	path('search_phone_number/', SearchPhoneNumber.as_view()),
    path('list_spam/', ListSpamNumbers.as_view())

    
]