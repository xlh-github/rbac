from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponse, redirect, reverse
import re

# 中间件
class RbacMidlleware(MiddlewareMixin):

    def process_request(self, request):
        # 获取当前访问的url
        url = request.path_info

        # 白名单
        for i in settings.WHITE_LIST:
            if re.match(i, url):
                return

        # 获取权限信息
        permission_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        print(permission_dict)



        # 登陆后没有权限
        if not permission_dict:
            return redirect(reverse('login'))

        request.current_menu_id = None
        # 面包屑
        request.breadcrumb_list = [
            {'title': '首页', 'url': '/index/'}
        ]

        # 需要登录但是不需要权限校验
        for i in settings.NO_PERMISSION_LIST:
            if re.match(i, url):
                return


        # 权限的校验
        for item in permission_dict.values():
            # {url   id   pid    }
            if re.match("^{}$".format(item['url']), url):
                # 要显示二级菜单的id  权限的id
                pid = item.get('pid')
                id = item.get('id')
                pname = item.get('pname')
                if pid:
                    # 当前访问的权限   是子权限  找父权限进行显示
                    request.current_menu_id = pid

                    request.breadcrumb_list.append(
                        {'title': permission_dict[pname]['title'], 'url': permission_dict[pname]['url']})
                    request.breadcrumb_list.append({'title': item['title'], 'url': item['url']})

                else:
                    # 当前访问的权限   是父权限  二级菜单   找自己进行显示

                    request.current_menu_id = id
                    request.breadcrumb_list.append({'title': item['title'], 'url': item['url']})

                return

        return HttpResponse('没有访问权限')
