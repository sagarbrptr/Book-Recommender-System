drop table django_session;
drop table django_migrations;
drop table django_admin_log;
drop table auth_user_user_permissions;
drop table auth_user_groups;
drop table auth_group_permissions;
drop table auth_user;
drop table auth_group;
drop table auth_permission;
drop table django_content_type;


-- After Deleting tables, staff users are also delted
-- run following in python shell to create new staff users
-- from django.contrib.auth.models import User
-- user = User.objects.create_user('admin', password = 'admin', is_staff = True)
-- user = User.objects.create_user('admin1', password = 'admin', is_staff = True)