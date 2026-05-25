"""DoingsForCustomersBot — customer assistant + Mini App entry + notifications."""

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
log = logging.getLogger("customers_bot")


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Open Doings (Mini App)",
                web_app=WebAppInfo(url=f"{settings.TG_WEBAPP_URL}/?role=customer"),
            )],
            [InlineKeyboardButton(text="📋 My active projects", callback_data="my_projects")],
            [InlineKeyboardButton(text="📝 Drafts", callback_data="drafts")],
        ]
    )


async def on_start(message: Message) -> None:
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)
    await message.answer(
        "👋 Welcome to <b>Doings</b> — your customer assistant.\n\n"
        "Open the Mini App to post projects and manage applicants.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


CUSTOMER_NOTIFICATIONS = {
    "new_application",
    "specialist_selected",
    "direct_offer_answered",
    "new_review",
}


def format_notification(payload: dict) -> str:
    t = payload.get("type", "")
    p = payload.get("payload", {})
    title = p.get("title", "your project")
    if t == "new_application":
        return f"📨 New application for <b>{title}</b>"
    if t == "specialist_selected":
        return f"✅ You selected a specialist for <b>{title}</b>"
    if t == "direct_offer_answered":
        outcome = "accepted ✅" if p.get("accepted") else "declined ❌"
        return f"🔔 Your direct offer was {outcome}"
    if t == "new_review":
        return f"⭐ New review on you (rating {p.get('rating', '?')})"
    return f"🔔 {t}"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not settings.TG_CUSTOMERS_BOT_TOKEN:
        log.error("TG_CUSTOMERS_BOT_TOKEN not set — exiting")
        return
    bot = Bot(settings.TG_CUSTOMERS_BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_start, F.text == "/menu")

    async def chat_lookup(user_id_str: str) -> int | None:
        return await chat_id_for_user_id(user_id_str, role=UserRole.CUSTOMER)

    log.info("CustomersBot started")
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
        run_notification_loop(bot, chat_lookup, format_notification, CUSTOMER_NOTIFICATIONS),
    )


if __name__ == "__main__":
    asyncio.run(main())
