
from decimal import Decimal
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from auctions.forms import LotForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import User, Lot, Bid, Watchlist, Comment
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    listing = Lot.objects.all()
    return render(request, "auctions/index.html", {
        'listing': listing,
    })


def active_listings(request):
    listing = Lot.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        'listing': listing,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            user_watchlist = Watchlist(user=user)
            user_watchlist.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class LotDetailView(generic.DetailView):
    model = Lot
    template_name = 'auctions/lot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            user_watchlist = Watchlist.objects.get(user=user)
            context["user_watchlist"] = user_watchlist.lots.all()
        return context


class CreateListingView(CreateView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/create_listing.html'

    def form_valid(self, form):
        lot = form.save(commit=False)
        lot.seller = User.objects.get(id=self.request.user.id)
        lot.save()
        messages.success(
            self.request, f'{lot.title} was created successfully!')
        return redirect('lot_detail', lot.pk)


class UserListingsView(generic.ListView):
    template_name = 'auctions/user_listings.html'

    def get_queryset(self):
        return User.objects.get(pk=self.kwargs['pk']).auction_lots.all()


class LotUpdateView(SuccessMessageMixin, UpdateView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/update_lot.html'
    success_message = "Updated successfully!"


class LotDeleteView(DeleteView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/delete_lot.html'
    success_message = "Deleted successfully!"
    permission_required = 'delete_lot'

    def get_success_url(self):
        return reverse('user_listings', args=[self.request.user.pk])

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(LotDeleteView, self).delete(request, *args, **kwargs)


class CategoryListingsView(generic.ListView):
    model = Lot
    template_name = 'auctions/category_listings.html'

    def get_queryset(self):
        return Lot.objects.filter(category=self.kwargs['category'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.kwargs["category"]
        return context


@login_required()
def place_bid(request, lot_id):
    lot = Lot.objects.get(pk=lot_id)
    current_bid = lot.bid.amount
    offer = Decimal(request.POST['offer'])

    if offer <= current_bid:
        messages.warning(request, 'Invalid price!',
                         extra_tags='alert alert-danger')
    else:
        new_bid = Bid(price=offer,
                      lot=lot, bidder=request.user)
        new_bid.save()
        lot.bid = new_bid.price
        lot.save()
        messages.success(request, 'Placed bid successfully!',
                         extra_tags='alert alert-primary')

    return redirect('lot_detail', pk=lot_id)


class UserWatchlistView(LoginRequiredMixin, generic.ListView):
    template_name = 'auctions/watchlist.html'

    def get_queryset(self):
        user = self.request.user
        watchlist = Watchlist.objects.get(user=user)
        lots = watchlist.lots.all()
        return lots


class CategoriesView(ListView):
    template_name = 'auctions/categories.html'

    def get_queryset(self):
        return set([lot.category for lot in Lot.objects.all()])


@login_required()
def update_watchlist(request, lot_id):
    lot = Lot.objects.get(pk=lot_id)
    url = reverse('watchlist', args=(request.user.id,))
    watchlist = Watchlist.objects.get(user=request.user)
    if lot in watchlist.lots.all():
        # Remove the lot to watchlist
        watchlist.lots.remove(lot)
        if request.META['HTTP_REFERER'] == f'http://127.0.0.1:8000/{request.user.id}/watchlist/':
            # If previous referer is 'watchlist', redirect to watchlist page.
            messages.success(request, f"Removed successfully!",
                             extra_tags='alert alert-primary')
            return redirect('watchlist', pk=request.user.id)
        messages.success(request, f"Removed successfully! <a href={url}>Go to see my watchlist</a>.",
                         extra_tags='alert alert-primary')
    else:
        # Add the lot from watchlist
        watchlist.lots.add(lot)
        messages.success(request, f"Added successfully! <a href={url}>Go to see my watchlist</a>.",
                         extra_tags='alert alert-primary')
    return redirect('lot_detail', pk=lot_id)


def close_auction(request, lot_id):
    lot = Lot.objects.get(pk=lot_id)
    if request.method == 'POST':
        lot.active = False
        bids = lot.bids.all()
        if bids:
            winner = bids.last().bidder
            lot.buyer = winner
        lot.save()
        return redirect('lot_detail', pk=lot_id)
    return render(request, 'auctions/close_auction.html', {'lot': lot, })


def comment(request, lot_id):
    lot = Lot.objects.get(pk=lot_id)
    content = request.POST.get('content')
    comment = Comment(commenter=request.user, lot=lot, content=content)
    comment.save()
    return redirect('lot_detail', pk=lot_id)
