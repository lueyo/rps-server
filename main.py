from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from models.room import Room
from services.game_service import GameService
from models.player import Player

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Initialize game service
game_service = GameService()

# Static files mounting removed because 'static' directory does not exist
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get():
   #Serve the main game page.
    #html_content = Path("templates/index.html").read_text()
    #return HTMLResponse(content=html_content)
    return "Not implemented"


@app.get("/room/{room_id}")
async def room_page(room_id: str):
    #Serve the game page for a specific room.
    #html_content = Path("templates/index.html").read_text()
    #return HTMLResponse(content=html_content)
    return "Not implemented"


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = None):
    """Handle WebSocket connections for game rooms."""
    await websocket.accept()

    try:
        # Add player to room
        player, room = game_service.add_player_to_room(room_id, username)
        player.websocket = websocket

        # Notify all players about new player
        for p in room.players:
            if p.websocket:
                await p.websocket.send_json(
                    {
                        "type": "player_joined",
                        "username": player.username,
                        "player_count": len(room.players),
                    }
                )

        # Start game if we have 2 players
        if len(room.players) == 2:
            room.game_state = "playing"
            for p in room.players:
                if p.websocket:
                    await p.websocket.send_json({"type": "game_start"})

        # Handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "choice":
                player.choice = message["choice"]

                # Notify player their choice was received
                await websocket.send_json(
                    {"type": "choice_made", "choice": player.choice}
                )

                # Check if both players have made choices
                if room.check_round_complete():
                    result = room.determine_winner()

                    # Send result to all players
                    for p in room.players:
                        if p.websocket:
                            await p.websocket.send_json(
                                {"type": "round_result", **result}
                            )

                    # Reset for next round
                    room.reset_round()

    except WebSocketDisconnect:
        # Remove player from room
        room_deleted = game_service.remove_player_from_room(room_id, player.uuid)

        # Notify remaining players
        for p in room.players:
            if p.websocket:
                await p.websocket.send_json(
                    {
                        "type": "player_left",
                        "message": f"Player {player.username} left the game",
                    }
                )

        # Reset game state if only one player left
        if len(room.players) == 1:
            room.game_state = "waiting"
            for p in room.players:
                if p.websocket:
                    await p.websocket.send_json({"type": "waiting_for_player"})


@app.get("/api/rooms")
async def get_rooms():
    """Get list of active rooms."""
    #return {"rooms": game_service.get_active_rooms()}
    pass


@app.get("/api/room/{room_id}")
async def get_room_state(room_id: str):
    """Get the current state of a room."""
    #return game_service.get_room_state(room_id)
    pass


# ping
@app.get("/ping")
async def ping():
    return {"message": "pong"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
