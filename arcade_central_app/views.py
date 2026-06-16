from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Game, Comment, FavoriteGame
from django.http import JsonResponse


# Create your views here.


def landing(request):
    return render(request, "landing.html")


def register_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        if not username or not password or not email or not confirm:
            messages.error(request, "All fields are required")
            return redirect("/register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("/register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("/register")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("/register")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        login(request, user)
        messages.success(
            request,
            "Welcome to Arcade Central! Your account has been created successfully.",
        )
        return redirect("/home")

    return render(request, "register.html")


def login_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("/admin_dashboard")

            return redirect("/home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("/login")

    return render(request, "login.html")


def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("/login")


def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("/")
    context = {"games": Game.objects.all()}

    return render(request, "admin_dashboard.html", context)


def add_game(request):
    if not request.user.is_superuser:
        return redirect("/")

    if request.method == "POST":
        errors = Game.objects.validator(request.POST)

        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect("/admin_dashboard")

        Game.objects.create(
            title=request.POST["title"].strip(),
            description=request.POST["description"].strip(),
            genre=request.POST["genre"].strip(),
            platform=request.POST["platform"].strip(),
            image_url=request.POST["image_url"].strip(),
        )

    return redirect("/admin_dashboard")


def delete_game(request, id):
    if not request.user.is_superuser:
        return redirect("/")

    game = Game.objects.get(id=id)
    game.delete()

    return redirect("/admin_dashboard")


def edit_game(request, id):
    if not request.user.is_superuser:
        return redirect("/")

    context = {"game": Game.objects.get(id=id), "games": Game.objects.all()}

    return render(request, "admin_dashboard.html", context)


def update_game(request, id):
    if not request.user.is_superuser:
        return redirect("/")

    game = Game.objects.get(id=id)

    if request.method == "POST":
        game.title = request.POST["title"]
        game.description = request.POST["description"]
        game.genre = request.POST["genre"]
        game.platform = request.POST["platform"]
        game.image_url = request.POST["image_url"]
        game.save()

    return redirect("/admin_dashboard")


def home(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    context = {"games": Game.objects.all()}

    return render(request, "home.html", context)


def game_details(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    context = {
        "game": Game.objects.get(id=id),
        "comments": Comment.objects.filter(game_id=id),
    }

    return render(request, "game_details.html", context)


def profile(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    favorites = FavoriteGame.objects.filter(user=request.user)

    context = {
        "user": request.user,
        "favorites_count": favorites.count(),
        "favorites": favorites,
    }

    return render(request, "profile.html", context)


def favorites(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    favorites = FavoriteGame.objects.filter(user=request.user)

    context = {"favorites": favorites}

    return render(request, "favorites.html", context)


def add_favorite(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    game = Game.objects.get(id=id)

    if FavoriteGame.objects.filter(user=request.user, game=game).exists():
        return redirect(f"/game/{id}/")

    FavoriteGame.objects.create(user=request.user, game=game)

    return redirect(f"/game/{id}/")


def add_comment(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    game = Game.objects.get(id=id)
    comment = request.POST.get("comment", "").strip()

    if comment:
        Comment.objects.create(user=request.user, game=game, comment=comment)

    return redirect(f"/game/{id}/")


def delete_comment(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    comment = Comment.objects.get(id=id)

    if comment.user != request.user:
        return redirect(f"/game/{comment.game.id}/")

    comment.delete()

    return redirect(f"/game/{comment.game.id}/")

def game_api(request, id):
    game = Game.objects.get(id=id)

    data = {
        "id": game.id,
        "title": game.title,
        "description": game.description,
        "genre": game.genre,
    }

    return JsonResponse(data)