from django.urls import path
from . import views



urlpatterns = [
    path('',views.home,name='home'),
    path('<int:auction_id>/bid/', views.bid, name='bid'),
    path('<int:auction_id>/', views.detail, name='detail'),
    path('accounts/register/',views.register,name='register'),
    
    #========================== For Cart =======================
    path('store/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
	# path('product/<str:pk>/', views.product, name='product'),
    
    path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
]