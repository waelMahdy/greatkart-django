from django.contrib import admin
from  .models import Product, ProductGalary, ReviewRating, Variation
import admin_thumbnails
# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalaryInLine(admin.TabularInline):
    model=ProductGalary  
    extra=1
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('category_name',)}
    list_display=( 'product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields={'slug':('product_name',)}
    inlines=[ProductGalaryInLine]
class VariationAdmin(admin.ModelAdmin):
    list_display=( 'product','variation_category','variation_value','is_active')
    list_editable=('is_active',)
    list_filter=( 'product','variation_category','variation_value','is_active')
class ReviewAdmin(admin.ModelAdmin):
    search_fields=['use']
  

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating,ReviewAdmin)
admin.site.register(ProductGalary)
