from django.conf import settings
from django.utils.module_loading import import_string
from django.urls import RegexURLResolver, RegexURLPattern
from collections import OrderedDict


def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    for item in urlpatterns:
        if isinstance(item, RegexURLResolver):
            if pre_namespace:
                if item.namespace:
                    namespace = "%s:%s" % (pre_namespace, item.namespace,)
                else:
                    namespace = pre_namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None
            #   none  '/^'
            recursion_urls(namespace, pre_url + item.regex.pattern, item.url_patterns, url_ordered_dict)
        else:

            if pre_namespace:  #  web
                name = "%s:%s" % (pre_namespace, item.name,)   # web:login
            else:
                name = item.name
            if not item.name:
                raise Exception('URL路由中必须设置name属性')
            # /^^login/$   /login/
            url = pre_url + item._regex
            url_ordered_dict[name] = {'name': name, 'url': url.replace('^', '').replace('$', '')}


def get_all_url_dict(ignore_namespace_list=None):
    """
    获取路由中所有的URL
    :return:

    { url别名：{ 'name' :URL别名  url ：路径 }  }
    """
    ignore_list = ignore_namespace_list or []
    url_ordered_dict = OrderedDict()

    md = import_string(settings.ROOT_URLCONF)
    urlpatterns = []


    """
    [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('web.urls')),
    url(r'^rbac/', include('rbac.urls', namespace='rbac')),
    
    视图函数 ： RegexURLPattern
    inculde  : RegexURLResolver
    
    ]
    """
    for item in md.urlpatterns:
        if isinstance(item, RegexURLResolver) and item.namespace in ignore_list:
            continue
        urlpatterns.append(item)
    recursion_urls(None, "/", urlpatterns, url_ordered_dict)
    return url_ordered_dict
