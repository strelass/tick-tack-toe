function activate_game(game_id, user, n, m) {
	var ws;

    window.requestAnimFrame = (function () {
        return window.requestAnimationFrame ||
            window.webkitRequestAnimationFrame ||
            window.mozRequestAnimationFrame ||
            window.oRequestAnimationFrame ||
            window.msRequestAnimationFrame ||
            function ( /* function */ callback, /* DOMElement */ element) {
            window.setTimeout(callback, 1000 / 600);
        };
    })();

    var game_status = {
        OPEN: "Waiting for opponent",
        START: "Game started",
        IN_PROGRESS: "Game in progress",
        DRAW: "Draw!",
        WINNER: "Winner: "
    };

	var canvas = document.getElementById("canvas"),
		ctx = canvas.getContext("2d"),
		maxH = ctx.canvas.height,
		maxW = ctx.canvas.width,
		cellH = maxH / n,
		cellW = maxW / m,
        lineWidth = 2,
        details = 50,
		turn = false,
        gamers = [],
        moves = [],
        first_gamer = -1,
        current_move = 0;

	function DrawGrid(){
        ctx.beginPath();
		for(var i = 0; i < m; i++) {
			for(var k = 0; k < n; k++) {
				ctx.rect(i*cellW, k*cellH, cellW, cellH);
			}
		}
		ctx.stroke();
	}

    //var points = [],
    //    currentPoint = 1,
    //    nextTime = new Date().getTime()+500,
    //    pace = 5;
    //function draw() {
    //
    //    if(new Date().getTime() > nextTime){
    //        nextTime = new Date().getTime() + pace;
    //        currentPoint++;
    //    }
    //    ctx.clearRect(0,0,canvas.width, canvas.height);
    //    ctx.beginPath();
    //    ctx.moveTo(points[0].x, points[0].y);
    //    ctx.lineWidth = 2;
    //    ctx.strokeStyle = '#2068A8';
    //    ctx.fillStyle = '#2068A8';
    //    for (var p = 1, plen = currentPoint; p < plen; p++) {
    //        ctx.lineTo(points[p].x, points[p].y);
    //    }
    //    ctx.stroke();
    //
    //    requestAnimFrame(draw);
    //}

	function DrawLineAnimated(xFrom, yFrom, xTo, yTo){
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
		ctx.moveTo(xFrom, yFrom);
		ctx.lineTo(xTo,	yTo);
		ctx.stroke();
        //devX = (xTo - xFrom) / details;
        //devY = (yTo - yFrom) / details;
        //points = [];
        //x = xFrom;
        //y = yFrom;
        //for (var i = 0; i < details; i++) {
        //    points.push({
        //        x: x,
        //        y: y
        //    });
        //    x += devX;
        //    y += devY;
        //}
        //draw();
	}

	function DrawCross(x, y){
		dev = 5;
		DrawLineAnimated(x*cellW + dev, y*cellH + dev, (x+1)*cellW - dev, (y+1)*cellH - dev);
		DrawLineAnimated(x*cellW + dev, (y+1)*cellH - dev, (x+1)*cellW - dev, y*cellH + dev);
	}

	function DrawEllipse(x, y) {
		dev = 5;
		halfCellH = cellH/2;
		halfCellW = cellW/2;
        radius = (cellW > cellH) ? cellH/2 : cellW/2;
        radius -= dev;
		ctx.beginPath();
        ctx.lineWidth = lineWidth;
		ctx.arc(x*cellW + halfCellW, y*cellH + halfCellH, radius, radius, Math.PI * 2, true);
		ctx.stroke();
	}

    function DrawMoves(num) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        DrawGrid();
        if (typeof num == 'undefined' || num < 0 || num > moves.length)
            num = moves.length;
        for(var i = 0; i < num; i++) {
            if (moves[i].gamer == first_gamer)
                DrawCross(moves[i].x, moves[i].y);
            else
                DrawEllipse(moves[i].x, moves[i].y);
        }
    }

    $(".gamer").each(function() {
        gamer_node = $(this);
        id = gamer_node.attr("id").replace("gamer-", "");
        gamer = {
            name: gamer_node.context.textContent,
            id: parseInt(id),
            node: gamer_node
        };
        gamers.push(gamer);
    });

	$(".move").each(function() {
        move = $(this).context.textContent;
        gamer = move.split("-")[0].slice(0, -1);
        y = parseInt(move.split("-")[1].split(":")[0]);
        x = parseInt(move.split("-")[1].split(":")[1]);
        if (first_gamer == -1)
            first_gamer = gamer;
        moves.push({
            x: x,
            y: y,
            gamer: gamer
        });
    }).click(function() {
        current_move = $(this);
        node = $(this).parent();
        count = 0;
        $.each(node.children("div.move"), function() {
            count++;
            if (current_move.is($(this))) {
                return false;
            }
        });
        DrawMoves(count);
    });

    DrawGrid();
    DrawMoves(-1);

    function getMousePos(evt) {
        var rect = canvas.getBoundingClientRect();
        return {
          x: evt.clientX - rect.left,
          y: evt.clientY - rect.top
        };
    }

	canvas.addEventListener('click', function(event) {
		if (turn) {
            position = getMousePos(event);
		    var absX = position.x,
		        absY = position.y;
		    var y = parseInt(absX / cellW, 10);
            var x = parseInt(absY / cellH, 10);

		    // Sending coordinates of current move
		    if (ws.readyState != WebSocket.OPEN) {
	            return false;
	        }
	        ws.send("%MOVE%" + x + ":" + y);
    	}
	}, false);

    function add_system_message(message, level) {
        log = document.createElement("li");
        log.setAttribute("class", "message " + level);
        log.innerHTML = message;
        $(".game-chat").append(log);
    }

    function add_message(name, message) {
        add_system_message(name + ": " + message, "message-simple");
    }

    function set_game_status(text) {
        $(".game-status").children()[0].textContent = text;
    }

    function find_gamer(id) {
        for(var i = 0; i < gamers.length; i++)
            if (gamers[i].id == id)
                return gamers[i];
        return null;
    }

	function alert_start(uid) {
		if (uid == user)
			turn = true;
        gamer = find_gamer(uid);
        add_system_message("Let the game begins. First turn for " + gamer.name + ".", "message-info");
	}

    function make_move(cellX, cellY, uid) {
        console.log("move by: " + uid + " me: " + user);
        if (uid == user) {
            DrawCross(cellY, cellX);
            turn = false;
        } else {
            DrawEllipse(cellY, cellX);
            turn = true;
        }
        move = document.createElement("div");
        move.setAttribute("class", "move");
        gamer = find_gamer(uid);
        move.innerHTML = gamer.name + " - " + cellX + ":" + cellY;
        $("#moves").append(move);
    }

    function alert_left(uid) {
        uid = parseInt(uid);
        gamer = find_gamer(uid);
        gamer_class = gamer.node.attr("class");
        if (gamer_class.indexOf("gamer") > -1) {
            gamer.node.attr("class", gamer_class.replace("online", "offline"));
        } else {
            gamer.node.remove();
            gamers = gamers.filter(function (el) {
                      return el.id !== uid;
                     }
            );
        }
        add_system_message(gamer.name + " has left the game.", "message-info");
    }

    function alert_join(uid, name) {
        uid = parseInt(uid);
        gamer = document.createElement("div");
        gamer.setAttribute("class", "gamer online");
        gamer.setAttribute("id", "gamer-"+uid);
        gamer.innerHTML = name;
        $("#gamers").append(gamer);
        gamers.push({
            id: uid,
            name: name,
            node: $("#gamer-"+uid)
        });
        add_system_message(name + " has joined the game.", "message-info");
    }

    function add_visitor(uid, name) {
        uid = parseInt(uid);
        gamer = document.createElement("div");
        gamer.setAttribute("class", "visitor");
        gamer.setAttribute("id", "gamer-"+uid);
        gamer.innerHTML = name;
        $("#visitors").append(gamer);
        gamers.push({
            id: uid,
            name: name,
            node: $("#gamer-"+uid)
        });
    }

    function update_user_status(uid, name) {
        uid = parseInt(uid);
        gamer = find_gamer(uid);
        if (!gamer) {
            add_visitor(uid, name);
            return;
        }
        gamer_class = gamer.node.attr("class");
        if (gamer_class.indexOf("gamer") > -1) {
            if (gamer_class.indexOf("offline") > -1) {
                gamer.node.attr("class", gamer_class.replace("offline", "online"));
            }
        }
    }

	function start_game_ws() {
        //ws = new WebSocket("ws://python-arrowtimetable.rhcloud.com:8000/game/" + game_id + "/");
        ws = new WebSocket("ws://127.0.0.1:8888/game/" + game_id + "/");
        ws.onmessage = function(event) {
            var message_data = JSON.parse(event.data);

            console.log(message_data);

            if (message_data.error)
                alert("Error");
            else
            switch (message_data.stat) {
                case "CONNECTED":
                    id = message_data.gamer_id;
                    name = message_data.gamer_name;
                    if (user != parseInt(id))
                        ws.send("%HERE%");
                    update_user_status(id, name);
                    add_system_message(name + " has joined the game.", "message-info");
                    break;
                case "GAME_STATUS":
                    if (user == parseInt(message_data.turn))
                        turn = true;
                    switch (message_data.game_status) {
                        case "OPEN":
                            set_game_status(game_status.OPEN);
                            break;
                        case "START":
                            set_game_status(game_status.START);
                            break;
                        case "IN_PROGRESS":
                            set_game_status(game_status.IN_PROGRESS);
                            break;
                        case "DRAW":
                            set_game_status(game_status.DRAW);
                            break;
                        case "WINNER":
                            winner = parseInt(message_data.winner);
                            winner = find_gamer(winner);
                            set_game_status(game_status.WINNER + winner.name);
                            break;
                    }
                    break;
                case "HANDSHAKE":
                    id = message_data.gamer_id;
                    name = message_data.gamer_name;
                    update_user_status(id, name);
                    break;
                case "JOIN":
                    id = message_data.gamer_id;
                    name = message_data.gamer_name;
                    alert_join(id, name);
                    break;
                case "LEFT":
                    name = message_data.leaver;
                    alert_left(name);
					break;
				case "START":
					uid = parseInt(message_data.turn);
					alert_start(uid);
					break;
            	case "PROCESS":
            		cellX = parseInt(message_data.x);
		            cellY = parseInt(message_data.y);
		            uid = message_data.uid;
                    make_move(cellX, cellY, uid);
            		break;
                case "MESSAGE":
                    add_message(
                        message_data.user,
                        message_data.message
                    );
                    break;
    			case "ERROR":
    				add_system_message(message_data.error, "message-error");
    				break;
				default:
                    alert("Unknown status");
            }
        };
        ws.onclose = function(){
            // Try to reconnect in 5 seconds
            setTimeout(function() {start_chat_ws()}, 5000);
        };
    }

	// Activating websockets
	if ("WebSocket" in window) {
        start_game_ws();
    } else {
    	alert("Your browser doesn't support websockets, please try to install new browser.")
        return false;
    }

    function send_chat_message(){
        var textarea = $("textarea#message_textarea");
        if (textarea.val() == "") {
            return false;
        }
        if (ws.readyState != WebSocket.OPEN) {
            return false;
        }
        ws.send("%MESS%" + textarea.val());
        textarea.val("");
    }

    $("#chat-send-button").click(function() {
        send_chat_message();
    });

    $("#message_textarea").keypress(function (event) {
        if (event.keyCode == 13) {
            send_chat_message();
            return false;
        }
    });

}