from django.contrib import admin
from rbac import models


# Register your models here.

class PermissionModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'url','name' ]
    list_editable = ['url', 'name']


admin.site.register(models.Permission, PermissionModelAdmin)
admin.site.register(models.Role)
# admin.site.register(models.User)
admin.site.register(models.Menu)


