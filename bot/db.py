"""
Thin data-access layer around the Supabase client.
All functions are sync (supabase-py is sync); they're called from
async handlers via run_in_executor where needed, but for MVP scale
we just call them directly (PostgREST calls are fast enough).
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from supabase import create_client, Client

from bot import config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)


# ---------------------------------------------------------------
# USERS
# ---------------------------------------------------------------
def get_user_by_telegram_id(telegram_id: int) -> Optional[dict]:
    res = (
        supabase.table("lingo_users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def create_user(
    telegram_id: int,
    ui_language: str = "en",
    first_name: str = "",
    last_name: str = "",
    username: str = "",
) -> dict:
    res = (
        supabase.table("lingo_users")
        .insert(
            {
                "telegram_id": telegram_id,
                "ui_language": ui_language,
                "native_language": "",
                "first_name": first_name or "",
                "last_name": last_name or "",
                "username": username or "",
            }
        )
        .execute()
    )
    return res.data[0]


def get_or_create_user(
    telegram_id: int,
    ui_language: str = "en",
    first_name: str = "",
    last_name: str = "",
    username: str = "",
) -> dict:
    user = get_user_by_telegram_id(telegram_id)
    if user:
        return user
    return create_user(telegram_id, ui_language, first_name, last_name, username)


def set_premium_filters(telegram_id: int, filter_gender, filter_interests: list) -> None:
    supabase.table("lingo_users").update(
        {"filter_gender": filter_gender, "filter_interests": filter_interests}
    ).eq("telegram_id", telegram_id).execute()


def update_user(telegram_id: int, fields: dict) -> dict:
    fields["last_active"] = datetime.now(timezone.utc).isoformat()
    res = (
        supabase.table("lingo_users")
        .update(fields)
        .eq("telegram_id", telegram_id)
        .execute()
    )
    return res.data[0] if res.data else None


def touch_last_active(telegram_id: int) -> None:
    supabase.table("lingo_users").update(
        {"last_active": datetime.now(timezone.utc).isoformat()}
    ).eq("telegram_id", telegram_id).execute()


def set_status(telegram_id: int, status: str) -> None:
    supabase.table("lingo_users").update({"status": status}).eq(
        "telegram_id", telegram_id
    ).execute()


def delete_user(telegram_id: int) -> None:
    supabase.table("lingo_users").delete().eq("telegram_id", telegram_id).execute()


# ---------------------------------------------------------------
# INTERESTS
# ---------------------------------------------------------------
def get_all_interests() -> list:
    res = supabase.table("lingo_interests").select("*").order("id").execute()
    return res.data or []


def set_user_interests(user_id: int, interest_codes: list) -> None:
    # clear existing
    supabase.table("lingo_user_interests").delete().eq("user_id", user_id).execute()
    if not interest_codes:
        return
    interests = get_all_interests()
    code_to_id = {i["code"]: i["id"] for i in interests}
    rows = [
        {"user_id": user_id, "interest_id": code_to_id[c]}
        for c in interest_codes
        if c in code_to_id
    ]
    if rows:
        supabase.table("lingo_user_interests").insert(rows).execute()


def get_user_interests(user_id: int) -> list:
    res = (
        supabase.table("lingo_user_interests")
        .select("interest_id, lingo_interests(code, name)")
        .eq("user_id", user_id)
        .execute()
    )
    return [row["lingo_interests"]["code"] for row in (res.data or []) if row.get("lingo_interests")]


# ---------------------------------------------------------------
# MATCHES
# ---------------------------------------------------------------
def create_match(user1_id: int, user2_id: int) -> dict:
    res = (
        supabase.table("lingo_matches")
        .insert({"user1_id": user1_id, "user2_id": user2_id})
        .execute()
    )
    return res.data[0]


def end_match(match_id: int, reason: str) -> None:
    match_res = supabase.table("lingo_matches").select("started_at").eq("id", match_id).execute()
    duration = None
    if match_res.data:
        started_at = datetime.fromisoformat(match_res.data[0]["started_at"].replace("Z", "+00:00"))
        duration = int((datetime.now(timezone.utc) - started_at).total_seconds())
    supabase.table("lingo_matches").update(
        {
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "end_reason": reason,
            "duration_seconds": duration,
        }
    ).eq("id", match_id).execute()


def log_message(match_id: int, sender_id: int) -> None:
    supabase.table("lingo_messages").insert(
        {"match_id": match_id, "sender_id": sender_id}
    ).execute()


# ---------------------------------------------------------------
# REPORTS
# ---------------------------------------------------------------
def create_report(reporter_id: int, reported_id: int, reason: str, match_id: Optional[int] = None) -> None:
    supabase.table("lingo_reports").insert(
        {
            "reporter_id": reporter_id,
            "reported_id": reported_id,
            "reason": reason,
            "match_id": match_id,
        }
    ).execute()
    # increment report_count on the reported user
    user_res = supabase.table("lingo_users").select("id, report_count").eq("id", reported_id).execute()
    if user_res.data:
        current = user_res.data[0]["report_count"] or 0
        supabase.table("lingo_users").update({"report_count": current + 1}).eq(
            "id", reported_id
        ).execute()


# ---------------------------------------------------------------
# PAYMENTS
# ---------------------------------------------------------------
def create_payment(user_id: int, method: str, amount, currency: str) -> dict:
    res = (
        supabase.table("lingo_payments")
        .insert(
            {
                "user_id": user_id,
                "method": method,
                "amount": amount,
                "currency": currency,
                "status": "pending",
            }
        )
        .execute()
    )
    return res.data[0]


def attach_payment_proof(payment_id: int, file_id: str) -> None:
    supabase.table("lingo_payments").update({"proof_screenshot_file_id": file_id}).eq(
        "id", payment_id
    ).execute()


def confirm_payment(payment_id: int, admin_note: str = "") -> dict:
    res = (
        supabase.table("lingo_payments")
        .update(
            {
                "status": "confirmed",
                "confirmed_at": datetime.now(timezone.utc).isoformat(),
                "admin_note": admin_note,
            }
        )
        .eq("id", payment_id)
        .execute()
    )
    return res.data[0] if res.data else None


def reject_payment(payment_id: int, admin_note: str = "") -> None:
    supabase.table("lingo_payments").update(
        {"status": "rejected", "admin_note": admin_note}
    ).eq("id", payment_id).execute()


def get_pending_payment_for_user(user_id: int) -> Optional[dict]:
    res = (
        supabase.table("lingo_payments")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def activate_premium(telegram_id: int, days: int) -> None:
    until = datetime.now(timezone.utc) + timedelta(days=days)
    supabase.table("lingo_users").update(
        {"premium": True, "premium_until": until.isoformat()}
    ).eq("telegram_id", telegram_id).execute()


# ---------------------------------------------------------------
# ADMIN STATS
# ---------------------------------------------------------------
def get_admin_stats() -> dict:
    res = supabase.table("lingo_admin_stats").select("*").limit(1).execute()
    return res.data[0] if res.data else {}


# ---------------------------------------------------------------
# ASYNC WRAPPERS
# ---------------------------------------------------------------
# supabase-py is a *synchronous* client. Every function above does a
# blocking network round-trip. Calling them directly from an async
# handler blocks the single-threaded event loop, which means ONE
# user's DB call stalls every other user's messages/button presses
# until it returns. That's the #1 cause of the bot slowing down
# under concurrent load.
#
# These wrappers push the blocking call onto a worker thread via
# asyncio.to_thread, so the event loop stays free to handle other
# updates while the network call is in flight. Handlers should
# `await db.<name>_async(...)` instead of calling the sync version
# directly wherever they're inside an async def.
def _make_async(fn):
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)
    wrapper.__name__ = f"{fn.__name__}_async"
    return wrapper


get_user_by_telegram_id_async = _make_async(get_user_by_telegram_id)
create_user_async = _make_async(create_user)
get_or_create_user_async = _make_async(get_or_create_user)
set_premium_filters_async = _make_async(set_premium_filters)
update_user_async = _make_async(update_user)
touch_last_active_async = _make_async(touch_last_active)
set_status_async = _make_async(set_status)
delete_user_async = _make_async(delete_user)

get_all_interests_async = _make_async(get_all_interests)
set_user_interests_async = _make_async(set_user_interests)
get_user_interests_async = _make_async(get_user_interests)

create_match_async = _make_async(create_match)
end_match_async = _make_async(end_match)
log_message_async = _make_async(log_message)

create_report_async = _make_async(create_report)

create_payment_async = _make_async(create_payment)
attach_payment_proof_async = _make_async(attach_payment_proof)
confirm_payment_async = _make_async(confirm_payment)
reject_payment_async = _make_async(reject_payment)
get_pending_payment_for_user_async = _make_async(get_pending_payment_for_user)
activate_premium_async = _make_async(activate_premium)

get_admin_stats_async = _make_async(get_admin_stats)