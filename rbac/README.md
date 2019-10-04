1. 拷贝rbac组件到新的项目中，并且要注册

1. 数据库的迁移

   1. 先删除rbac下migrations下的除了init之外的文件

   2. 修改用户表

      1. ```python
         class User(models.Model):
             """
             用户表
             """
             # name = models.CharField(max_length=32, verbose_name='用户名')
             # pwd = models.CharField(max_length=32, verbose_name='密码')
             roles = models.ManyToManyField(Role, blank=True)   # 关联用类

             class Meta:
                 abstract = True     # 执行数据库迁移命令时不会生成具体的表，这张表做基类
         ```

      1. 在新项目中用户表要去继承User

   3. 执行数据库迁移的命令

1. 在根的urlconf中添加rbac的路由

   ```python
   url(r'rbac/', include('rbac.urls', namespace='rbac'))
   ```

1. 角色管理  添加角色

2. 菜单管理   给权重

3. 权限管理

   1. 录入权限信息
   2. 分配好菜单和父权限

4. 分配权限

   1. 给角色分配权限

   1. 给用户分配角色

1. 加上权限的控制

   1. 加中间件

   1. 权限的配置放在settings中

      ```python
      # 权限存放在session中的KEY
      PERMISSION_SESSION_KEY = 'permission'

      # 菜单存放在session中的KEY
      MENU_SESSION_KEY = 'menu'

      WHITE_LIST = [
          r'^/login/$',
          r'^/reg/$',
          r'^/admin/.*',
      ]

      NO_PERMISSION_LIST = [
          r'^/index/$',
      ]
      ```

   1. 修改登录函数

      校验成功后权限信息的初始化

      ```python
      from rbac.service.permission import init_permission
      # 登录成功后
      init_permission(request,obj)
      ```

1. 应用上二级菜单

     在母板中使用 menu inclusion_tag

   ```
   {% load rbac %}
   {% menu request %}
   ```

   引入css、js的效果

2. 路径导航

   ```
   {% breadcrumb request %}
   ```

3. 权限控制到按钮

```html
{% load rbac %}
{% if request|has_permission:'add_customer' %}
    <a class="btn btn-sm btn-primary" style="margin-bottom: 5px"
       href="{% reverse_url request 'add_customer' %}">添加</a>

{% endif %}
```

