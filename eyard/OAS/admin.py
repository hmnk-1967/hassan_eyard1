from django.contrib import admin
from OAS.models import Auction,Bid,Customer,Product,Order,OrderItem,ShippingAddress
# Register your models here.

admin.site.register(Auction)
admin.site.register(Bid)



# ======= For Cart ================

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
