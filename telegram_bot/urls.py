from django.urls import path, include
from rest_framework.routers import DefaultRouter
from telegram_bot.viewsets import SeriesViewSet, PostViewSet, SignupViewSet, CustomMessageViewSet

router = DefaultRouter()
router.register(r'series', SeriesViewSet, base_name="Series")
router.register(r'post', PostViewSet, base_name="Post")
router.register(r'signup', SignupViewSet, base_name="Signup")
router.register(r'custom-message', CustomMessageViewSet, base_name="CustomMessage")

urlpatterns=[
	path('',include(router.urls))
]