import os
from datetime import datetime, timedelta
from urllib.parse import quote

import requests

from app.db.connection import get_connection

API_BASE_URL = os.getenv("SYNC_API_BASE_URL", "").strip().rstrip("/")


def _request_json(path, params=None):
    if not API_BASE_URL:
        raise RuntimeError("SYNC_API_BASE_URL is not configured")

    response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=10)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def _fallback_member_total_xp(rsn):
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


def _fallback_all_member_xp():
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


def _fallback_inactive_members():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 0 ORDER BY rsn"
        ).fetchall()
        return [dict(row) for row in rows]


def _fallback_inactive_members_by_rank_and_days(rank, days):
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


def _fallback_members_by_rank(rank):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 1 AND rank = ? ORDER BY rsn",
            (rank,),
        ).fetchall()
        return [dict(row) for row in rows]


def _fallback_member_xp_history(rsn, days=7):
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


def _fallback_private_members():
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


def get_member_total_xp(rsn):
    if API_BASE_URL:
        try:
            return _request_json(f"/member/{quote(rsn)}")
        except requests.RequestException:
            return None
    return _fallback_member_total_xp(rsn)


def get_all_member_xp():
    if API_BASE_URL:
        try:
            return _request_json("/members") or []
        except requests.RequestException:
            return []
    return _fallback_all_member_xp()


def get_inactive_members():
    if API_BASE_URL:
        try:
            return _request_json("/inactive-members") or []
        except requests.RequestException:
            return []
    return _fallback_inactive_members()


def get_inactive_members_by_rank_and_days(rank, days):
    if API_BASE_URL:
        try:
            return _request_json("/inactive-members-by-rank", params={"rank": rank, "days": days}) or []
        except requests.RequestException:
            return []
    return _fallback_inactive_members_by_rank_and_days(rank, days)


def get_members_by_rank(rank):
    if API_BASE_URL:
        try:
            return _request_json(f"/members-by-rank/{quote(rank)}") or []
        except requests.RequestException:
            return []
    return _fallback_members_by_rank(rank)


def get_member_xp_history(rsn, days=7):
    if API_BASE_URL:
        try:
            return _request_json(f"/xp-history/{quote(rsn)}", params={"days": days}) or []
        except requests.RequestException:
            return []
    return _fallback_member_xp_history(rsn, days)


def get_private_members():
    if API_BASE_URL:
        try:
            return _request_json("/private-members") or []
        except requests.RequestException:
            return []
    return _fallback_private_members()