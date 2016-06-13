function activate_game(game_id, user, n, m) {
	var ws;

	var canvas = document.getElementById("canvas"),
		ctx = canvas.getContext("2d"),
		maxH = ctx.canvas.height,
		maxW = ctx.canvas.width,
		cellH = maxH / n,
		cellW = maxW / m,
		turn = false,
        gamers = [];

	function DrawGrid(){
		for(var i = 0; i < m; i++) {
			for(var k = 0; k < n; k++) {
				ctx.rect(i*cellW, k*cellH, cellW, cellH);
			}
		}
		ctx.stroke(); 
	}

	function DrawLineAnimated(xFrom, yFrom, xTo, yTo){
		ctx.beginPath();
		ctx.moveTo(xFrom, yFrom);
		ctx.lineTo(xTo,	yTo);
		ctx.stroke();
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
		ctx.arc(x*cellW + halfCellW, y*cellH + halfCellH, radius, radius, Math.PI * 2, true);
		ctx.stroke();
	}

	DrawGrid();

    $(".gamer").each(function() {
        gamer_node = $(this);
        gamer = {
            name: gamer_node.context.textContent,
            id: parseInt(gamer_node.attr("id")),
            node: gamer_node
        };
        gamers.push(gamer);
    });

	$(".move").each(function() {
        move = $(this).context.textContent;
        gamer = move.split("-")[0].slice(0, -1);
        y = parseInt(move.split("-")[1].split(":")[0]);
        x = parseInt(move.split("-")[1].split(":")[1]);
        if (gamer == find_gamer(user).name) {
            DrawCross(x, y);
        } else {
            DrawEllipse(x, y);
        }
    });

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
	        ws.send(x + ":" + y);
    	}
	}, false);

    function add_system_message(message, level) {
        log = document.createElement("li");
        log.setAttribute("class", "message " + level);
        log.innerHTML = message;
        $(".game-chat").append(log);
    }

    function alert_join(gamer_id, gamer_name) {
        if (!find_gamer(gamer_id)) {
            gamer = document.createElement("div");
            gamer.setAttribute("class", "gamer_name");
            gamer.setAttribute("id", "gamer_id");
            gamer.innerHTML = name;

            gamers.push({
                id: gamer_id,
                name: gamer_name,
                node: gamer
            });
            $("#gamers").append(gamer);
        }
        add_system_message(gamer_name + " has joined the game.", "message-info");
    }

    function find_gamer(id) {
        for(var i = 0; i < gamers.length; i++)
            if (gamers[i].id == id)
                return gamers[i];
        return null;
    }

    function alert_left(gamer_id) {
        gamer = find_gamer(gamer_id);
        gamer.node.remove();
        leaver_name = gamer.name;
        gamers = gamers.filter(function (el) {
                      return el.id !== gamer_id;
                 }
        );
        add_system_message(leaver_name + " has left the game.", "message-info");
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

    function alert_resume(uid) {
        if (uid == user) {
            turn = true;
        }
    }

	function end_game(winner) {
        add_system_message("The Winner is " + winner + "!", "message-success");
	}

	function start_game_ws() {
        ws = new WebSocket("ws://127.3.77.1:8888/game/" + game_id + "/");
        ws.onmessage = function(event) {
            var message_data = JSON.parse(event.data);

            console.log(message_data);

            if (message_data.error)
                alert("Error");
            else
            switch (message_data.stat) {
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
                case "RESUME":
                    uid = parseInt(message_data.turn);
                    alert_resume(uid);
                    break;
        		case "WINNER":
        			end_game(message_data.winner);
        			break;
                case "DRAW":
        			alert("draw!");
            		ws.close();
        			break;
    			case "error":
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

}