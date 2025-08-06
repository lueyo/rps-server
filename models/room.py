from typing import List, Optional, Dict, Any
from models.player import Player


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[Player] = []
        self.game_state = "waiting"  # waiting, playing, finished
        self.round_results = []

    def add_player(self, player: Player) -> bool:
        """Add a player to the room. Returns True if successful, False if room is full."""
        if len(self.players) >= 2:
            return False
        # if username already exists, gen an 6 digit random id username-{id}
        if player.username in [p.username for p in self.players]:
            player.username = f"{player.username}-{len([p for p in self.players if p.username.startswith(player.username)])}"
        self.players.append(player)
        return True

    def remove_player(self, player_uuid: str):
        """Remove a player from the room."""
        self.players = [p for p in self.players if p.uuid != player_uuid]

    def get_player_by_uuid(self, uuid: str) -> Optional[Player]:
        """Get a player by their UUID."""
        return next((p for p in self.players if p.uuid == uuid), None)

    def reset_round(self):
        """Reset the round for all players."""
        for player in self.players:
            player.choice = None
        self.game_state = "playing"

    def check_round_complete(self) -> bool:
        """Check if all players have made their choices."""
        return all(player.choice is not None for player in self.players)

    def determine_winner(self) -> Dict[str, Any]:
        """Determine the winner of the current round."""
        if len(self.players) != 2:
            return {"error": "Not enough players"}

        p1, p2 = self.players
        choices = {"rock": 0, "paper": 1, "scissors": 2}

        if p1.choice not in choices or p2.choice not in choices:
            return {"error": "Invalid choices"}

        c1, c2 = choices[p1.choice], choices[p2.choice]

        if c1 == c2:
            return {
                "winner": "tie",
                "choices": {p1.username: p1.choice, p2.username: p2.choice},
            }

        if (c1 - c2) % 3 == 1:
            return {
                "winner": p1.username,
                "choices": {p1.username: p1.choice, p2.username: p2.choice},
            }
        else:
            return {
                "winner": p2.username,
                "choices": {p1.username: p1.choice, p2.username: p2.choice},
            }

    def is_full(self) -> bool:
        """Check if the room is full."""
        return len(self.players) >= 2

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "game_state": self.game_state,
            "players": [player.to_dict() for player in self.players],
            "round_results": self.round_results,
        }
