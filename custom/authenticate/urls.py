from django.urls import path

from. import views
app_name="authenticate"

urlpatterns=[
    path('',views.home,name="home"),
    path('Signup',views.signup,name="signup"),
    path('Login',views.login,name="login"),
    path('User',views.userhome,name="user"),
    path('activate_eamil/<uidb64>/<token>/<res>/',views.activate,name="activate"),
    path('logout',views.logout,name="logout"),
    path('verify',views.verifymail,name="verify"),
    path('User/changePassword',views.changepassword,name="chnage"),
    path('User/final',views.final,name="final"),
    path('User/forgot',views.forgot,name="forgot"),
    path('User/reset_password',views.resetpassword,name="resetpassword"),
     path('user/create_new_password/<uidb64>/<token>/<res>/',views.createnewpassword,name="newpassword"),
    path('chnageit',views.changeit,name="passchange"),

]