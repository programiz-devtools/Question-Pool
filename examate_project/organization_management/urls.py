from django.urls import path
from .views import OrganizationsView,SwitchUserAccountStatus,DeleteUserAccount,SearchUser


urlpatterns = [
   path('users/',OrganizationsView.as_view(),name='organizations'),
   path('searchuser/',SearchUser.as_view(),name = 'search_user'),
   path('switch-user-status/<int:pk>/', SwitchUserAccountStatus.as_view(), name='switch_user_account_status'), 
   path('delete-user/<int:pk>/', DeleteUserAccount.as_view(), name='delete_user_account'),
 
]