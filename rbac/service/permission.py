from django.conf import settings


def init_permission(request, obj):
    # 保存权限信息
    # 查询
    permission_query = obj.roles.all().filter(permissions__url__isnull=False).values('permissions__title',
                                                                                     'permissions__url',
                                                                                     'permissions__menu__name',
                                                                                     'permissions__menu__icon',
                                                                                     'permissions__menu__weight',
                                                                                     'permissions__menu__id',
                                                                                     'permissions__id',
                                                                                     'permissions__parent_id',
                                                                                     'permissions__name',
                                                                                     'permissions__parent__name',
                                                                                     ).distinct()

    print(permission_query)
    # 存放权限信息的列表
    permission_dict = {}
    # 存放菜单信息的列表
    menu_dict = {}

    for item in permission_query:
        # 将权限信息放入permission_list
        permission_dict[item['permissions__name']] = {'url': item['permissions__url'],
                                                      'pid': item['permissions__parent_id'],
                                                      'pname': item['permissions__parent__name'],
                                                      'id': item['permissions__id'],
                                                      'title': item['permissions__title'],
                                                      }

        # 放入菜单信息
        menu_id = item.get('permissions__menu__id')

        # 不是菜单
        if not menu_id:
            continue

        if menu_id not in menu_dict:
            menu_dict[menu_id] = {'name': item['permissions__menu__name'],
                                  'icon': item['permissions__menu__icon'],
                                  'weight': item['permissions__menu__weight'],
                                  'children': [{'id': item['permissions__id'], 'title': item['permissions__title'],
                                                'url': item['permissions__url']}]}
        else:
            menu_dict[menu_id]['children'].append(
                {'id': item['permissions__id'], 'title': item['permissions__title'], 'url': item['permissions__url']})

    # 权限信息放入session
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict

    # 菜单信息放入session
    request.session[settings.MENU_SESSION_KEY] = menu_dict
