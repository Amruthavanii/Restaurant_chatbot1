from django.contrib import admin
from django.urls import path, include
from orders import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),

    path('menu/', views.menu_view, name='menu'),
    path('profile/', views.profile_view, name='profile'),

    path('api/menu/', views.api_menu, name='api_menu'),
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/order/', views.api_order, name='api_order'),
    path('api/chat/', views.api_chat, name='api_chat'),
        path('admin/', admin.site.urls),

    path('api/menu/', views.api_menu, name='api_menu'),

    path('api/chatbot-response/', views.chatbot_response, name='chatbot_response'),

    
    
]
