from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("active_listings", views.active_listings, name="active_listings"),
    path("listings/<int:pk>/", views.LotDetailView.as_view(), name="lot_detail"),
    path("create_listing/", views.CreateListingView.as_view(), name="create_listing"),
    path("<int:pk>/listings/", views.UserListingsView.as_view(), name="user_listings"),
    path("<int:pk>/update_lot/", views.LotUpdateView.as_view(), name="update_lot"),
    path("<int:pk>/delete_lot/", views.LotDeleteView.as_view(), name="delete_lot"),
    path("listings/<str:category>/",
         views.CategoryListingsView.as_view(), name="category_listings"),
    path("<int:lot_id>/place_bid/", views.place_bid, name="place_bid"),
    path("<int:pk>/watchlist/", views.UserWatchlistView.as_view(), name="watchlist"),
    path("listings/<int:lot_id>/update_watchlist/",
         views.update_watchlist, name="update_watchlist"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("<int:lot_id>/close/",
         views.close_auction, name="close_auction"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
