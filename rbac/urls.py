from django.conf.urls import url
from rbac import views

urlpatterns = [
    # 角色
    url(r'^role/list/$', views.role_list, name='role_list'),
    url(r'^role/add/$', views.role_change, name='role_add'),
    url(r'^role/edit/(\d+)/$', views.role_change, name='role_edit'),
    url(r'^role/del/(\d+)/$', views.role_del, name='role_del'),
    # 菜单
    url(r'^menu/list/$', views.menu_list, name='menu_list'),
    url(r'^menu/add/$', views.menu_change, name='menu_add'),
    url(r'^menu/edit/(\d+)/$', views.menu_change, name='menu_edit'),
    url(r'^(menu)/del/(\d+)/$', views.delete, name='menu_del'),

    # 权限
    url(r'^permission/add/$', views.permission_change, name='permission_add'),
    url(r'^permission/edit/(\d+)/$', views.permission_change, name='permission_edit'),
    url(r'^(permission)/del/(\d+)/$', views.delete, name='permission_del'),

    url(r'^multi/permissions/$', views.multi_permissions, name='multi_permissions'),

    url(r'^distribute/permissions/$', views.distribute_permissions, name='distribute_permissions'),

]
