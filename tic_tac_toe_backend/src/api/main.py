from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status as http_status
from typing import List
from datetime import datetime

from src.api.game_logic import (
    initial_board,
    get_game_status,
    play_move,
    Player,
    GameStatus,
)
from src.api.database import (
    create_game,
    update_game,
    get_game,
    list_games,
)
from src.api.schemas import (
    GameCreateRequest,
    GameMoveRequest,
    GameStatusResponse,
    GameHistoryItem,
)

app = FastAPI(
    title="Tic Tac Toe Backend API",
    description="RESTful API for managing and playing Tic Tac Toe games.",
    version="1.0.0",
    openapi_tags=[
        {"name": "game", "description": "Game management and play"},
        {"name": "history", "description": "View previous games"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Health Check", tags=["game"])
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.post(
    "/games/",
    response_model=GameStatusResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Start a new game",
    tags=["game"]
)
def start_game(
    req: GameCreateRequest,
):
    """
    Starts a new Tic Tac Toe game.

    - **first_player**: Optional, 'X' or 'O', defaults to 'X'.
    - Returns: Initial GameStatusResponse.
    """
    # Start with default player (just for extensibility)
    board = initial_board()
    moves = []
    status = get_game_status(board)
    game_id = create_game(moves, board, status, None)
    game = get_game(game_id)
    return GameStatusResponse(
        id=game["id"],
        board=game["board"],
        moves=game["moves"],
        status=game["status"],
        winner=game["winner"],
        created_at=game["created_at"],
        finished_at=game["finished_at"],
    )

# PUBLIC_INTERFACE
@app.get(
    "/games/{game_id}/",
    response_model=GameStatusResponse,
    summary="Get status of a game",
    tags=["game"]
)
def get_game_status_api(game_id: int):
    """
    Fetch current state of game by ID.

    - **game_id**: Game identifier
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameStatusResponse(
        id=game["id"],
        board=game["board"],
        moves=game["moves"],
        status=game["status"],
        winner=game["winner"],
        created_at=game["created_at"],
        finished_at=game["finished_at"],
    )

# PUBLIC_INTERFACE
@app.post(
    "/games/{game_id}/move/",
    response_model=GameStatusResponse,
    summary="Make a move",
    tags=["game"],
)
def make_move(game_id: int, req: GameMoveRequest):
    """
    Play a move for a game.

    - **player**: 'X' or 'O'
    - **row**: Row index 0-2
    - **col**: Col index 0-2
    - **game_id**: Which game to update
    - Returns: Updated GameStatusResponse or error if invalid
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    board = game["board"]
    moves = game["moves"]
    status = game["status"]

    # Cannot play if already won or drawn
    if status in [GameStatus.WINNER_X, GameStatus.WINNER_O, GameStatus.DRAW]:
        raise HTTPException(
            status_code=400,
            detail="Game is already finished."
        )

    # Validate and apply move
    updated_board, error = play_move(board, req.row, req.col, Player(req.player))
    if error:
        raise HTTPException(status_code=400, detail=error)
    moves = moves + [dict(player=req.player, row=req.row, col=req.col)]

    new_status = get_game_status(updated_board)
    new_winner = None
    if new_status == GameStatus.WINNER_X:
        new_winner = Player.X
    elif new_status == GameStatus.WINNER_O:
        new_winner = Player.O

    finished_timestamp = None
    if new_status in [GameStatus.WINNER_X, GameStatus.WINNER_O, GameStatus.DRAW]:
        finished_timestamp = datetime.utcnow().isoformat()

    update_game(
        game_id,
        moves,
        updated_board,
        new_status,
        new_winner,
        finished_at=finished_timestamp,
    )
    game = get_game(game_id)
    return GameStatusResponse(
        id=game["id"],
        board=game["board"],
        moves=game["moves"],
        status=game["status"],
        winner=game["winner"],
        created_at=game["created_at"],
        finished_at=game["finished_at"],
    )

# PUBLIC_INTERFACE
@app.get(
    "/games/",
    response_model=List[GameHistoryItem],
    summary="List recent games",
    tags=["history"],
)
def list_game_history(limit: int = 20, offset: int = 0):
    """
    Returns a paginated list of the most recent games.
    """
    games = list_games(limit=limit, offset=offset)
    return [
        GameHistoryItem(
            id=g["id"],
            status=g["status"],
            winner=g["winner"],
            created_at=g["created_at"],
            finished_at=g["finished_at"],
        )
        for g in games
    ]
