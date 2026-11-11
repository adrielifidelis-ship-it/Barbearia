from django.contrib import admin
from django.urls import path
from barbearia import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.agendamento, name='agendamento'),
    path('api/horarios/', views.buscar_horarios, name='buscar_horarios'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('painel/', views.painel_barbeiro, name='painel'),
]