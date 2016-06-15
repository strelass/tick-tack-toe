from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from tick_tack_toe.forms import SimpleGameForm
from tick_tack_toe.models import Game
from tick_tack_toe.utils import join_game, json_response, try_to_make_move, make_move


def home(request):
    return render(request, 'home.html', context={})


@login_required
def lobby(request):
    form = SimpleGameForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            game = form.save(commit=False)
            game.turn = request.user
            with transaction.atomic():
                game.save()
                game.participants.add(request.user)
            return HttpResponseRedirect(reverse("game", kwargs={'game_id': game.id}))
    games = Game.objects.all().order_by('-id')
    paginator = Paginator(games, 10)
    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
        page = 1
    except EmptyPage:
        games = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    context = {
        "form": form,
        "games": games,
        "pages": range(1, paginator.num_pages+1),
        "active_page": int(page),
    }
    return render(request, "tick_tack_toe/lobby.html", context)


@login_required
def game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    user = request.user
    if game.status == "OPEN" and request.user not in game.participants.all():
        join_game(game.id, user.id, user.username)
        with transaction.atomic():
            game.status = "START"
            game.participants.add(user)
            game.turn = game.participants.first()
            game.save()
    moves = game.move_set.all()
    participants = game.participants.all()
    context = {
        "game": game,
        "moves": moves,
        "participants": participants,
    }
    return render(request, "tick_tack_toe/game.html", context)


@csrf_exempt
def make_move_view_api(request, game_id):

    if not request.method == "POST":
        return json_response({"error": "Please use POST."})

    api_key = request.POST.get("api_key")

    if api_key != settings.API_KEY:
        return json_response({"error": "Please pass a correct API key."})

    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return json_response({"error": "No such game."})

    try:
        gamer = User.objects.get(id=request.POST.get("gamer_id"))
    except User.DoesNotExist:
        return json_response({"error": "No such user."})

    move = request.POST.get("move")

    if not move:
        return json_response({"error": "No move found."})

    result = try_to_make_move(
        game,
        move,
        gamer
    )
    print "MAKE_MOVE_VIEW_API: %s, res: %s" % (move, result)
    if "error" in result:
        return json_response(result["error"])

    make_move(
        game.id,
        gamer.id,
        result["x"],
        result["y"],
    )

    return json_response({"status": "ok"})
