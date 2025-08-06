import json
from typing import Dict, Any, List
from models.player import Player
from models.room import Room


class GameService:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def get_or_create_room(self, room_id: str) -> Room:
        """Get existing room or create new one."""
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id)
        return self.rooms[room_id]

    def add_player_to_room(
        self, room_id: str, username: str = None
    ) -> tuple[Player, Room]:
        """Add a player to a room. Returns (player, room) tuple."""
        room = self.get_or_create_room(room_id)

        if room.is_full():
            raise ValueError("Room is full")

        player = Player(username)
        room.add_player(player)

        return player, room

    def remove_player_from_room(self, room_id: str, player_uuid: str) -> bool:
        """Remove a player from a room. Returns True if room was deleted."""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]
        room.remove_player(player_uuid)

        if len(room.players) == 0:
            del self.rooms[room_id]
            return True

        return False

    def make_choice(
        self, room_id: str, player_uuid: str, choice: str
    ) -> Dict[str, Any]:
        """Process a player's choice and return round result if complete."""
        if room_id not in self.rooms:
            return {"error": "Room not found"}

        room = self.rooms[room_id]
        player = room.get_player_by_uuid(player_uuid)

        if not player:
            return {"error": "Player not found"}

        player.choice = choice

        if room.check_round_complete():
            result = room.determine_winner()
            room.round_results.append(result)
            room.reset_round()
            return result

        return {"status": "waiting", "message": "Waiting for other player"}

    def get_room_state(self, room_id: str) -> Dict[str, Any]:
        """Get the current state of a room."""
        if room_id not in self.rooms:
            return {"error": "Room not found"}

        return self.rooms[room_id].to_dict()

    def get_active_rooms(self) -> List[str]:
        """Get list of active room IDs."""
        return list(self.rooms.keys())

    def cleanup_empty_rooms(self):
        """Remove empty rooms."""
        empty_rooms = [
            room_id for room_id, room in self.rooms.items() if len(room.players) == 0
        ]
        for room_id in empty_rooms:
            del self.rooms[room_id]
