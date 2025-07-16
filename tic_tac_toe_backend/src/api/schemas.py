from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Player(str, Enum):
    X = "X"
    O = "O"

class GameStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DRAW = "DRAW"
    WINNER_X = "WINNER_X"
    WINNER_O = "WINNER_O"

# PUBLIC_INTERFACE
class MoveSchema(BaseModel):
    player: Player = Field(..., description="Player making the move")
    row: int = Field(..., ge=0, le=2, description="Row index (0-2)")
    col: int = Field(..., ge=0, le=2, description="Column index (0-2)")

# PUBLIC_INTERFACE
class GameCreateRequest(BaseModel):
    first_player: Optional[Player] = Field(Player.X, description="Player to make the first move")

# PUBLIC_INTERFACE
class GameMoveRequest(BaseModel):
    player: Player = Field(..., description="Player who is making the move")
    row: int = Field(..., ge=0, le=2)
    col: int = Field(..., ge=0, le=2)

# PUBLIC_INTERFACE
class GameStatusResponse(BaseModel):
    id: int = Field(..., description="Game ID")
    board: List[List[Optional[Player]]] = Field(..., description="Current board state")
    moves: List[MoveSchema] = Field(..., description="Moves made")
    status: GameStatus = Field(..., description="Current game status")
    winner: Optional[Player] = Field(None, description="Who won, if any")
    created_at: Optional[str] = Field(None, description="Creation datetime")
    finished_at: Optional[str] = Field(None, description="Finish datetime (if any)")

# PUBLIC_INTERFACE
class GameHistoryItem(BaseModel):
    id: int = Field(...)
    status: GameStatus = Field(...)
    winner: Optional[Player] = Field(None)
    created_at: Optional[str]
    finished_at: Optional[str]
