from auctions.forms import LotForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import User, Lot
from django.views import generic


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


class CreateListingView(generic.CreateView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/create_listing.html'

    def form_valid(self, form):
        lot = form.save(commit=False)
        lot.seller = User.objects.get(id=self.request.user.id)
        lot.save()
        return redirect('lot_detail', lot.pk)


# def show_user_listings(request):
#     user_id = request.user.pk
#     lots = User.objects.get(pk=user_id).lots
#     template = f'auctions/{user_id}/listings.html'
#     render(request, template, {
#         'lots': lots,
#     })

class UserListingsView(generic.ListView):
    template_name = 'auctions/user_listings.html'

    def get_queryset(self):
        return User.objects.get(pk=self.request.user.pk).lots.all()


class LotUpdateView(generic.UpdateView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/update_lot.html'


class LotDeleteView(generic.DeleteView):
    model = Lot
    form_class = LotForm
    template_name = 'auctions/delete_lot.html'

    def get_success_url(self):
        return reverse('user_listings', self.request.user.pk)


def place_bid(request):
    pass
