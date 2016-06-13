function activate_game(game_id, user, n, m) {
	var ws;

	var canvas = document.getElementById("canvas"),
		ctx = canvas.getContext("2d"),
		canvasLeft = canvas.offsetLeft,
		canvasTop = canvas.offsetTop,
		maxH = ctx.canvas.height,
		maxW = ctx.canvas.width,
		cellH = maxH / n,
		cellW = maxW / m,
		turn = false;

	function DrawGrid(){
		for(var i = 0; i < n; i++) {
			for(var k = 0; k < m; k++) {
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
		ctx.beginPath();
		ctx.arc(x*cellW + halfCellW, y*cellH + halfCellH, halfCellW - dev, halfCellH - dev, Math.PI * 2, true);
		ctx.stroke();
	}

	DrawGrid();

	$(".move").each(function() {
        move = $(this).context.textContent;
        gamer = parseInt(move.split("-")[0]);
        x = parseInt(move.split("-")[1].split(":")[0]);
        y = parseInt(move.split("-")[1].split(":")[1]);
        if (gamer == user) {
            DrawCross(x, y);
        } else {
            DrawEllipse(x, y);
        }
    });

	canvas.addEventListener('click', function(event) {
		if (turn) {
		    var absX = event.pageX - canvasLeft,
		        absY = event.pageY - canvasTop;
		    var y = parseInt(absX / cellH, 10);
		    var x = parseInt(absY / cellW, 10);

		    // Sending coordinates of current move
		    if (ws.readyState != WebSocket.OPEN) {
	            return false;
	        }
	        ws.send(x + ":" + y);
    	}
	}, false);

    function alert_join(name) {
        gamer = document.createElement("div");
        gamer.setAttribute("class", "gamer");
        gamer.innerHTML = name;
        $("#gamers").append(gamer);
        alert(name + " joined your game!")
    }

    function alert_left(name) {
         $(".gamer").each(function() {
             if ($(this).context.innerText == name)
                $(this).remove();
         });
        alert(name + " left from your game!");
    }

	function alert_start(uid) {
		if (uid == user)
			turn = true;
		alert("The game has began. First turn for " + uid + ".");
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
        move.innerHTML = uid + " - " + cellX + ":" + cellY;
        $("#moves").append(move);
    }

    function alert_resume(uid) {
        if (uid == user) {
            turn = true;
        }
    }

	function end_game(winner) {
		alert("Winner is " + winner);
	}

	function start_game_ws() {
		// url = document.URL.split("/")[0];
		// ws = new WebSocket("ws://" + url + ":8888/" + game_id + "/");
        ws = new WebSocket("ws://127.0.0.1:8888/game/" + game_id + "/");
        ws.onmessage = function(event) {
            var message_data = JSON.parse(event.data);

            console.log(message_data);

            if (message_data.error)
                alert("Error");
            else
            switch (message_data.stat) {
                case "JOIN":
                    name = message_data.newbie;
                    alert_join(name);
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
    				alert(message_data.error);
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