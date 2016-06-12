from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
import redis

from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.contrib.auth.models import User
from tick_tack_toe.forms import GameForm, SimpleGameForm
from tick_tack_toe.models import Thread, Game
from tick_tack_toe.utils import *


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
    paginator = Paginator(games, 25)
    page = request.GET.get('page')
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "games": games,
    }
    return render(request, "privatemessages/lobby.html", context)


@login_required
def game_view(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.user not in game.participants.all() and game.status != "OPEN":
        return HttpResponseRedirect(reverse("lobby"))
    else:
        if game.status == "OPEN" and game.participants.count() <= 1:
            with transaction.atomic():
                game.status = "IN_PROGRESS"
                game.save()
                game.participants.add(request.user)
        join_game(game.id, request.user.username)
    moves = game.move_set.all()
    participants = game.participants.all()
    context = {
        "game": game,
        "moves": moves,
        "participants": participants,
    }
    return render(request, "privatemessages/game.html", context)


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

    if "error" in result:
        return json_response(result["error"])

    make_move(
        game.id,
        gamer.id,
        result["x"],
        result["y"],
    )

    return json_response({"status": "ok"})


def send_message_view(request):
    if not request.method == "POST":
        return HttpResponse("Please use POST.")

    if not request.user.is_authenticated():
        return HttpResponse("Please sign in.")

    message_text = request.POST.get("message")

    if not message_text:
        return HttpResponse("No message found.")

    if len(message_text) > 10000:
        return HttpResponse("The message is too long.")

    recipient_name = request.POST.get("recipient_name")

    try:
        recipient = User.objects.get(username=recipient_name)
    except User.DoesNotExist:
        return HttpResponse("No such user.")

    if recipient == request.user:
        return HttpResponse("You cannot send messages to yourself.")

    thread_queryset = Thread.objects.filter(
        participants=recipient
    ).filter(
        participants=request.user
    )

    if thread_queryset.exists():
        thread = thread_queryset[0]
    else:
        thread = Thread.objects.create()
        thread.participants.add(request.user, recipient)

    send_message(
        thread.id,
        request.user.id,
        message_text,
        request.user.username
    )

    return HttpResponseRedirect(
        reverse('messages')
    )


@csrf_exempt
def send_message_api_view(request, thread_id):
    if not request.method == "POST":
        return json_response({"error": "Please use POST."})

    api_key = request.POST.get("api_key")

    if api_key != settings.API_KEY:
        return json_response({"error": "Please pass a correct API key."})

    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        return json_response({"error": "No such thread."})

    try:
        sender = User.objects.get(id=request.POST.get("sender_id"))
    except User.DoesNotExist:
        return json_response({"error": "No such user."})

    message_text = request.POST.get("message")

    if not message_text:
        return json_response({"error": "No message found."})

    if len(message_text) > 10000:
        return json_response({"error": "The message is too long."})

    send_message(
        thread.id,
        sender.id,
        message_text
    )

    return json_response({"status": "ok"})


def messages_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("Please sign in.")

    threads = Thread.objects.filter(
        participants=request.user
    ).order_by("-last_message")

    if not threads:
        return render_to_response('privatemessages/private_messages.html',
                                  {},
                                  context_instance=RequestContext(request))

    r = redis.StrictRedis()

    user_id = str(request.user.id)

    for thread in threads:
        thread.partner = thread.participants.exclude(id=request.user.id)[0]

        thread.total_messages = r.hget(
            "".join(["thread_", str(thread.id), "_messages"]),
            "total_messages"
        )

    return render_to_response('privatemessages/private_messages.html',
                              {
                                  "threads": threads,
                              },
                              context_instance=RequestContext(request))


def chat_view(request, thread_id):
    if not request.user.is_authenticated():
        return HttpResponse("Please sign in.")

    thread = get_object_or_404(
        Thread,
        id=thread_id,
        participants__id=request.user.id
    )

    messages = thread.message_set.order_by("-datetime")[:100]

    user_id = str(request.user.id)

    r = redis.StrictRedis()

    messages_total = r.hget(
        "".join(["thread_", thread_id, "_messages"]),
        "total_messages"
    )

    messages_sent = r.hget(
        "".join(["thread_", thread_id, "_messages"]),
        "".join(["from_", user_id])
    )

    if messages_total:
        messages_total = int(messages_total)
    else:
        messages_total = 0

    if messages_sent:
        messages_sent = int(messages_sent)
    else:
        messages_sent = 0

    messages_received = messages_total - messages_sent

    partner = thread.participants.exclude(id=request.user.id)[0]

    tz = request.COOKIES.get("timezone")
    if tz:
        timezone.activate(tz)

    return render_to_response('privatemessages/chat.html',
                              {
                                  "thread_id": thread_id,
                                  "thread_messages": messages,
                                  "messages_total": messages_total,
                                  "messages_sent": messages_sent,
                                  "messages_received": messages_received,
                                  "partner": partner,
                              },
                              context_instance=RequestContext(request))
