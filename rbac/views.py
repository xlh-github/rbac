from django.shortcuts import render, redirect, reverse, HttpResponse
from rbac import models
from rbac.forms import RoleForm, MenuForm, PermissionForm, MultiPermissionForm
from crm.models import UserProfile


def role_list(request):
    all_roles = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'all_roles': all_roles})

# 添加与编辑公用
def role_change(request, edit_id=None):
    obj = models.Role.objects.filter(pk=edit_id).first()

    form_obj = RoleForm(instance=obj)
    if request.method == 'POST':
        form_obj = RoleForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:role_list'))

    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def role_del(request, del_id):
    models.Role.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbac:role_list'))


from django.db.models import Q


def menu_list(request):
    all_menus = models.Menu.objects.all()

    mid = request.GET.get('mid')
    if mid:
        # all_permissions = models.Permission.objects.filter(menu_id=mid)
        all_permissions = models.Permission.objects.filter(Q(menu_id=mid) | Q(parent__menu_id=mid)).values()
    else:
        all_permissions = models.Permission.objects.all().values()

    permission_dict = {}

    for i in all_permissions:

        menu_id = i.get('menu_id')
        p_id = i.get('id')
        if menu_id:
            permission_dict[p_id] = i
            i['children'] = []

    for i in all_permissions:
        pid = i.get('parent_id')
        if pid:
            permission_dict[pid]['children'].append(i)

    print(permission_dict)

    return render(request, 'rbac/menu_list.html',
                  {'mid': mid, 'all_menus': all_menus, 'all_permissions': permission_dict})


def menu_change(request, edit_id=None):
    obj = models.Menu.objects.filter(pk=edit_id).first()

    form_obj = MenuForm(instance=obj)
    if request.method == 'POST':
        form_obj = MenuForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))

    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def permission_change(request, edit_id=None):
    obj = models.Permission.objects.filter(pk=edit_id).first()

    form_obj = PermissionForm(instance=obj)
    if request.method == 'POST':
        form_obj = PermissionForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))

    return render(request, 'rbac/form.html', {'form_obj': form_obj})


def delete(request, table, del_id):
    model_class = getattr(models, table.capitalize())

    if model_class:
        model_class.objects.filter(pk=del_id).delete()
        return redirect(reverse('rbac:menu_list'))

    else:
        return HttpResponse('不能删除')


from django.forms import modelformset_factory, formset_factory
from rbac.service.routes import get_all_url_dict


def multi_permissions(request):
    """
    批量操作权限
    :param request:
    :return:
    """
    post_type = request.GET.get('type')

    # 编辑和删除
    FormSet = modelformset_factory(models.Permission, MultiPermissionForm, extra=0)
    # 新增
    AddFormSet = formset_factory(MultiPermissionForm, extra=0)

    # 数据库中所有的权限
    permissions = models.Permission.objects.all()
    # 路由系统中所有的URL  权限
    router_dict = get_all_url_dict(ignore_namespace_list=['admin', ])

    # 数据库中所有的权限的别名的集合
    permissions_name_set = set([i.name for i in permissions])

    # 路由系统中所有的权限的别名的集合
    router_name_set = set(router_dict.keys())
    # 新增权限的name_set
    add_name_set = router_name_set - permissions_name_set

    add_formset = AddFormSet(initial=[row for name, row in router_dict.items() if name in add_name_set])

    if request.method == 'POST' and post_type == 'add':
        add_formset = AddFormSet(request.POST)
        if add_formset.is_valid():
            permission_obj_list = [models.Permission(**i) for i in add_formset.cleaned_data]
            query_list = models.Permission.objects.bulk_create(permission_obj_list)
            add_formset = AddFormSet()
            for i in query_list:
                permissions_name_set.add(i.name)

    # 要删除的权限
    del_name_set = permissions_name_set - router_name_set
    del_formset = FormSet(queryset=models.Permission.objects.filter(name__in=del_name_set))

    update_name_set = permissions_name_set & router_name_set
    update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    if request.method == 'POST' and post_type == 'update':
        update_formset = FormSet(request.POST)
        if update_formset.is_valid():
            update_formset.save()
            update_formset = FormSet(queryset=models.Permission.objects.filter(name__in=update_name_set))

    return render(
        request,
        'rbac/multi_permissions.html',
        {
            'del_formset': del_formset,
            'update_formset': update_formset,
            'add_formset': add_formset,
        }
    )


def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        user.roles.set(request.POST.getlist('roles'))

    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = models.Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 所有的用户
    user_list = UserProfile.objects.all()

    # 当前用户所拥有角色
    user_has_roles = UserProfile.objects.filter(id=uid).values('id', 'roles')

    """
    用户所拥有的角色id
    user_has_roles_dict =  { 角色id : None  }
    """
    user_has_roles_dict = {item['roles']: None for item in user_has_roles}

    # 所有的角色
    role_list = models.Role.objects.all()

    if rid:
        role_has_permissions = models.Role.objects.filter(id=rid, permissions__id__isnull=False).values('id',
                                                                                                        'permissions')
    elif uid and not rid:
        # 当前的用户
        user = UserProfile.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        # 当前用户 所有有的角色和所有权限的id
        role_has_permissions = user.roles.filter(permissions__id__isnull=False).values('id', 'permissions')
        role_has_permissions = user.roles.filter(permissions__id__isnull=False).values('id', 'permissions')
    else:
        role_has_permissions = []

    # 当前用户所有的权限id
    """
    role_has_permissions_dict =  {    权限的ID ：None}
    """

    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    all_menu_list = []

    queryset = models.Menu.objects.values('id', 'name')  # 【   {id   name   }】
    menu_dict = {}

    """
    all_menu_list = [   {id   name  children:[
        {  'id', 'title', 'menu_id'  children : [
             {'id', 'title', 'parent_id' }
        ]  }
    ]  } 
    
    ,{'id': None, 'title': '其他', 'children': [
         {'id', 'title', 'parent_id' }
    ]}]
    
    
    menu_dict = { 
            菜单的id:  {id   name  children:[
                {  'id', 'title', 'menu_id'  children : [
                     {'id', 'title', 'parent_id' }
                ]  }
            ]  } ,
            None:  {'id': None, 'title': '其他', 'children': [
             {'id', 'title', 'parent_id' }
            ]}
    }
    """

    for item in queryset:  # {id   name   }
        item['children'] = []  # {id   name  children:[]   }
        menu_dict[item['id']] = item
        all_menu_list.append(item)

    other = {'id': None, 'title': '其他', 'children': []}
    all_menu_list.append(other)
    menu_dict[None] = other

    # 所有的父权限
    root_permission = models.Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    root_permission_dict = {}
    """
      root_permission_dict = {
            父权限的id :  {  'id', 'title', 'menu_id'  children : [  {'id', 'title', 'parent_id' } ]  }
      }
    """

    for per in root_permission:  # {  'id', 'title', 'menu_id' }
        per['children'] = []  # {  'id', 'title', 'menu_id'  children : []  }
        nid = per['id']
        menu_id = per['menu_id']
        root_permission_dict[nid] = per
        menu_dict[menu_id]['children'].append(per)

    # 可能是子权限
    node_permission = models.Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:   # {'id', 'title', 'parent_id' }
        pid = per['parent_id']
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        root_permission_dict[pid]['children'].append(per)

    return render(
        request,
        'rbac/distribute_permissions.html',
        {
            'user_list': user_list,
            'role_list': role_list,
            'all_menu_list': all_menu_list,
            'user_has_roles_dict': user_has_roles_dict,
            'role_has_permissions_dict': role_has_permissions_dict,
            'uid': uid,
            'rid': rid
        }
    )
