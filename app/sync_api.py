import os
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException

from app.db.connection import get_connection

app = FastAPI(title="TIN Sync API", version="1.0.0")


def _member_total_xp_query(rsn: str):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank, x.total_xp, x.timestamp
            FROM members m
            LEFT JOIN xp_snapshots x ON m.id = x.member_id
            WHERE m.rsn = ? COLLATE NOCASE AND x.id = (
                SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id
            )
            """,
            (rsn,),
        ).fetchone()
        return dict(row) if row else None


def _all_member_xp_query():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank, x.total_xp, x.timestamp
            FROM members m
            LEFT JOIN xp_snapshots x ON m.id = x.member_id
            WHERE m.active = 1 AND x.id = (
                SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id
            )
            ORDER BY x.total_xp DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def _inactive_members_query():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 0 ORDER BY rsn"
        ).fetchall()
        return [dict(row) for row in rows]


def _inactive_members_by_rank_and_days_query(rank: str, days: int):
    with get_connection() as conn:
        cutoff_date = datetime.now() - timedelta(days=days)
        rows = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank,
                   latest.total_xp as current_xp,
                   latest.timestamp as current_timestamp,
                   old.total_xp as xp_at_cutoff,
                   old.timestamp as old_timestamp
            FROM members m
            LEFT JOIN xp_snapshots latest ON m.id = latest.member_id
                AND latest.id = (SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id)
            LEFT JOIN xp_snapshots old ON m.id = old.member_id
                AND old.timestamp <= ?
                AND old.id = (SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id AND timestamp <= ?)
            WHERE m.active = 1
            AND m.rank = ? COLLATE NOCASE
            AND latest.total_xp = old.total_xp
            ORDER BY latest.timestamp ASC
            """,
            (cutoff_date, cutoff_date, rank),
        ).fetchall()
        return [dict(row) for row in rows]


def _members_by_rank_query(rank: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 1 AND rank = ? ORDER BY rsn",
            (rank,),
        ).fetchall()
        return [dict(row) for row in rows]


def _member_xp_history_query(rsn: str, days: int = 7):
    with get_connection() as conn:
        cutoff_date = datetime.now() - timedelta(days=days)
        rows = conn.execute(
            """
            SELECT x.timestamp, x.total_xp
            FROM xp_snapshots x
            JOIN members m ON x.member_id = m.id
            WHERE m.rsn = ? COLLATE NOCASE AND x.timestamp >= ?
            ORDER BY x.timestamp
            """,
            (rsn, cutoff_date),
        ).fetchall()
        return [dict(row) for row in rows]


def _private_members_query():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank
            FROM members m
            LEFT JOIN xp_snapshots x ON m.id = x.member_id
                AND x.id = (SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id)
            WHERE m.active = 1 and x.total_xp IS NULL
            ORDER BY m.rsn
            """
        ).fetchall()
        return [dict(row) for row in rows]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/members")
def members():
    return _all_member_xp_query()


@app.get("/member/{rsn}")
def member_total_xp(rsn: str):
    payload = _member_total_xp_query(rsn)
    if payload is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return payload


@app.get("/leaderboard")
def leaderboard():
    return _all_member_xp_query()


@app.get("/inactive-members")
def inactive_members():
    return _inactive_members_query()


@app.get("/inactive-members-by-rank")
def inactive_members_by_rank(rank: str, days: int = 30):
    return _inactive_members_by_rank_and_days_query(rank, days)


@app.get("/members-by-rank/{rank}")
def members_by_rank(rank: str):
    return _members_by_rank_query(rank)


@app.get("/xp-history/{rsn}")
def member_xp_history(rsn: str, days: int = 7):
    return _member_xp_history_query(rsn, days)


@app.get("/private-members")
def private_members():
    return _private_members_query()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.sync_api:app", host="0.0.0.0", port=int(os.getenv("SYNC_API_PORT", "8000")), reload=False)
