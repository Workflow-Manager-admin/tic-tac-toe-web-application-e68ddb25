import os
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import json

DB_URL = os.getenv("TIC_TAC_TOE_DATABASE_URL", "sqlite:///./tic_tac_toe.db")

Base = declarative_base()
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    moves = Column(Text, nullable=False)  # JSON-encoded list of moves dicts
    board = Column(Text, nullable=False)  # JSON-encoded 2d board
    status = Column(String(32), nullable=False)
    winner = Column(String(8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Context manager for session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# PUBLIC_INTERFACE
def create_game(moves, board, status, winner=None) -> int:
    """Create a new game and return its id."""
    with get_db() as db:
        game = Game(
            moves=json.dumps(moves),
            board=json.dumps(board),
            status=status,
            winner=winner
        )
        db.add(game)
        db.commit()
        db.refresh(game)
        return game.id

# PUBLIC_INTERFACE
def update_game(game_id: int, moves, board, status, winner=None, finished_at=None) -> None:
    """Update an existing game."""
    with get_db() as db:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            raise ValueError("Game not found")
        game.moves = json.dumps(moves)
        game.board = json.dumps(board)
        game.status = status
        game.winner = winner
        if finished_at:
            game.finished_at = finished_at
        db.commit()

# PUBLIC_INTERFACE
def get_game(game_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single game by id."""
    with get_db() as db:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None
        return {
            "id": game.id,
            "moves": json.loads(game.moves),
            "board": json.loads(game.board),
            "status": game.status,
            "winner": game.winner,
            "created_at": game.created_at.isoformat() if game.created_at else None,
            "finished_at": game.finished_at.isoformat() if game.finished_at else None,
        }

# PUBLIC_INTERFACE
def list_games(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Return a list of games, most recent first."""
    with get_db() as db:
        games = db.query(Game).order_by(Game.id.desc()).limit(limit).offset(offset).all()
        return [
            {
                "id": g.id,
                "moves": json.loads(g.moves),
                "board": json.loads(g.board),
                "status": g.status,
                "winner": g.winner,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "finished_at": g.finished_at.isoformat() if g.finished_at else None,
            }
            for g in games
        ]
