"""DoingsForDoersBot — specialist assistant + Mini App entry + notifications."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.core.config import get_settings
from app.models.user import UserRole
from bots.common.auth import update_chat_id
from bots.common.db import SessionLocal
from bots.common.lookup import chat_id_for_user_id
from bots.common.notifications import run_notification_loop

settings = get_settings()
log = logging.getLogger("doers_bot")


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Open Doings (Mini App)",
                web_app=WebAppInfo(url=f"{settings.TG_WEBAPP_URL}/?role=specialist"),
            )],
            [InlineKeyboardButton(text="📋 My active projects", callback_data="my_projects")],
            [InlineKeyboardButton(text="⭐ My rating", callback_data="my_rating")],
        ]
    )


async def on_start(message: Message) -> None:
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)
    await message.answer(
        "👋 Welcome to <b>Doings</b> — your specialist assistant.\n\n"
        "Use the Mini App for the full experience, or browse from here.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


SPECIALIST_NOTIFICATIONS = {
    "application_accepted",
    "application_rejected",
    "project_completed",
    "direct_offer_received",
    "new_review",
}


def format_notification(payload: dict) -> str:
    t = payload.get("type", "")
    p = payload.get("payload", {})
    title = p.get("title", "your project")
    if t == "application_accepted":
        return f"🎉 You were selected for: <b>{title}</b>"
    if t == "application_rejected":
        return f"❌ Customer chose someone else for <b>{title}</b>"
    if t == "project_completed":
        return f"✅ Project completed: <b>{title}</b>. Leave a review when you can."
    if t == "direct_offer_received":
        return f"📨 Direct offer received for <b>{title}</b>"
    if t == "new_review":
        return f"⭐ New review (rating {p.get('rating', '?')})"
    return f"🔔 {t}"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not settings.TG_DOERS_BOT_TOKEN:
        log.error("TG_DOERS_BOT_TOKEN not set — exiting")
        return
    bot = Bot(settings.TG_DOERS_BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_start, F.text == "/menu")

    async def chat_lookup(user_id_str: str) -> int | None:
        return await chat_id_for_user_id(user_id_str, role=UserRole.SPECIALIST)

    log.info("DoersBot started")
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
        run_notification_loop(bot, chat_lookup, format_notification, SPECIALIST_NOTIFICATIONS),
    )


if __name__ == "__main__":
    asyncio.run(main())
