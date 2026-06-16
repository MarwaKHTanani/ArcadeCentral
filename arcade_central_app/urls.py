from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing),
    path('login/', views.login_page),
    path('register/', views.register_page),
    path('logout/', views.logout_user),
    path("admin_dashboard/", views.admin_dashboard),
    path("add-game/", views.add_game),
    path("delete-game/<int:id>/", views.delete_game),
    path("edit-game/<int:id>/", views.edit_game),
    path("update-game/<int:id>/", views.update_game),
    path('home/', views.home),
    path('game/<int:id>/', views.game_details),
    path('profile/', views.profile),
    path('favorites/', views.favorites),
    path('add-favorite/<int:id>/', views.add_favorite),
    path('add-comment/<int:id>/', views.add_comment),
    path('delete-comment/<int:id>/', views.delete_comment),
    path("api/games/<int:id>/", views.game_api),
]