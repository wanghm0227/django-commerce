
from decimal import Decimal
from django.contrib.messages.views import SuccessMessageMixin
from auctions.forms import LotForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import User, Lot, Bid
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages


def index(request):
    listing = Lot.objects.all()
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
        lot = self.object
        context["highest_bid"] = lot.bids.order_by("-price").first()
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
        return User.objects.get(pk=self.kwargs['pk']).lots.all()


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


def place_bid(request, lot_id):
    lot = Lot.objects.get(pk=lot_id)
    bids = lot.bids.all()
    offer = Decimal(request.POST['offer'])
    if bids:
        highest_bid = bids.order_by('-price').first().price.amount
    else:
        highest_bid = lot.bid.amount
    if offer <= highest_bid:
        messages.warning(request, 'Invalid price!',
                         extra_tags='alert alert-danger')
    else:
        new_bid = Bid(price=offer,
                      lot=lot, bidder=request.user)
        new_bid.save()
        lot.bids.add(new_bid)
        messages.success(request, 'Placed bid successfully!',
                         extra_tags='alert alert-primary')

    return redirect('lot_detail', pk=lot_id)
