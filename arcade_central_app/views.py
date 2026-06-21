from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Game, Comment, FavoriteGame, Notification
from django.http import JsonResponse

# Create your views here.


def landing(request):
    games = list(Game.objects.order_by("created_at")[:3])
    hero_games = list(Game.objects.order_by("-created_at")[:4])

    context = {
        "games": games,
        "hero_games": hero_games,
        "games_count": Game.objects.count(),
        "comments_count": Comment.objects.count(),
        "users_count": User.objects.count(),
    }
    return render(request, "landing.html", context)


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
    context = {
        "games_count": Game.objects.count(),
    }

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

    return render(request, "login.html", context)


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
        for user in User.objects.filter(is_superuser=False):

            Notification.objects.create(
                user=user,
                type="new_game",
                message=f"A new game '{request.POST['title']}' has been added to Arcade Central!",
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

    favorites = FavoriteGame.objects.filter(user=request.user)

    user_favorites = favorites.values_list("game_id", flat=True)
    games = Game.objects.all()
    genres = list(games.values_list("genre", flat=True).distinct())
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        "games": games,
        "user_favorites": user_favorites,
        "genres": genres,
        "unread_count": unread_count,
    }

    return render(request, "home.html", context)


def game_details(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    game = Game.objects.get(id=id)
    comments = Comment.objects.filter(game=game, parent=None).order_by("-created_at")
    is_favorite = FavoriteGame.objects.filter(user=request.user, game=game).exists()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    context = {
        "game": game,
        "comments": comments,
        "is_favorite": is_favorite,
        "unread_count": unread_count,
    }

    return render(request, "game_details.html", context)


def profile(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    favorites = FavoriteGame.objects.filter(user=request.user)
    comments_count = Comment.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    context = {
        "user": request.user,
        "favorites_count": favorites.count(),
        "favorites": favorites,
        "comments_count": comments_count,
        "unread_count": unread_count,
    }

    return render(request, "profile.html", context)


def add_favorite(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "unauthorized"})

    game = Game.objects.get(id=id)

    favorite = FavoriteGame.objects.filter(user=request.user, game=game).first()
    if favorite:
        favorite.delete()
        return JsonResponse({"status": "removed"})

    FavoriteGame.objects.create(user=request.user, game=game)

    return JsonResponse({"status": "added"})


def add_comment(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    game = Game.objects.get(id=id)
    comment = request.POST.get("comment", "").strip()
    parent_id = request.POST.get("parent_id")

    if comment:
        parent = Comment.objects.get(id=parent_id) if parent_id else None
        Comment.objects.create(
            user=request.user, game=game, comment=comment, parent=parent
        )
        if parent and parent.user != request.user:
            Notification.objects.create(
                user=parent.user,
                type="reply",
                message=f"{request.user.username} replied to your comment on '{game.title}'!",
            )

    return redirect(f"/game/{id}/")


def delete_comment(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")

    comment = Comment.objects.get(id=id)

    if comment.user != request.user:
        return redirect(f"/game/{comment.game.id}/")

    comment.delete()

    return redirect(f"/game/{comment.game.id}/")


def unread_notifications_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "unauthorized"})

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"count": count})


def remove_favorite(request, id):
    if not request.user.is_authenticated:
        return redirect("/login")
    favorite = FavoriteGame.objects.get(user=request.user, game_id=id)
    if favorite:
        favorite.delete()
    return redirect("/profile/")


def notifications(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()

    notifications.filter(is_read=False).update(is_read=True)

    context = {
        "notifications": notifications,
        "unread_count": unread_count,
    }
    return render(request, "notifications.html", context)


def comments_api(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "unauthorized"})

    comments = Comment.objects.filter(game_id=id, parent=None).order_by("created_at")
    data = []
    for comment in comments:
        replies = []
        for reply in comment.replies.all():
            replies.append(
                {
                    "id": reply.id,
                    "user": reply.user.username,
                    "text": reply.comment,
                    "time": reply.created_at.strftime("%b %d, %Y"),
                    "is_mine": reply.user == request.user,
                }
            )
        data.append(
            {
                "id": comment.id,
                "user": comment.user.username,
                "text": comment.comment,
                "time": comment.created_at.strftime("%b %d, %Y"),
                "is_mine": comment.user == request.user,
                "replies": replies,
            }
        )
    return JsonResponse({"comments": data})
