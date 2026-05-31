"""DoingsForDoersBot — specialist assistant + Mini App entry + notifications."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.core.config import get_settings
from app.core.i18n import DEFAULT as DEFAULT_LANG
from app.models.user import UserRole
from bots.common.auth import get_user_by_tg, update_chat_id
from bots.common.db import SessionLocal
from bots.common.i18n import t
from bots.common.lang import ensure_user_language
from bots.common.lang_command import handle_lang_command
from bots.common.lookup import chat_id_for_user_id
from bots.common.notifications import run_notification_loop

settings = get_settings()
log = logging.getLogger("doers_bot")


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t("shared.open_app", lang),
                web_app=WebAppInfo(url=f"{settings.TG_WEBAPP_URL}/?role=specialist"),
            )],
            [InlineKeyboardButton(
                text=t("doers.menu.my_projects", lang), callback_data="my_projects"
            )],
            [InlineKeyboardButton(
                text=t("doers.menu.my_rating", lang), callback_data="my_rating"
            )],
        ]
    )


async def on_start(message: Message) -> None:
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)
        user = await get_user_by_tg(session, message.from_user.id)
        lang = await ensure_user_language(session, user, message.from_user)
    await message.answer(
        t("doers.welcome", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang),
    )


SPECIALIST_NOTIFICATIONS = {
    "application_accepted",
    "application_rejected",
    "project_completed",
    "direct_offer_received",
    "new_review",
}


def format_notification(payload: dict, lang: str = DEFAULT_LANG) -> str:
    notif_type = payload.get("type", "")
    p = payload.get("payload", {})
    title = p.get("title") or t("notifications.fallback_title", lang)
    if notif_type == "application_accepted":
        return t("notifications.application_accepted", lang, title=title)
    if notif_type == "application_rejected":
        return t("notifications.application_rejected", lang, title=title)
    if notif_type == "project_completed":
        return t("notifications.project_completed", lang, title=title)
    if notif_type == "direct_offer_received":
        return t("notifications.direct_offer_received", lang, title=title)
    if notif_type == "new_review":
        return t("notifications.new_review_specialist", lang, rating=p.get("rating", "?"))
    return t("notifications.fallback", lang, type=notif_type)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not settings.TG_DOERS_BOT_TOKEN:
        log.error("TG_DOERS_BOT_TOKEN not set — exiting")
        return
    bot = Bot(settings.TG_DOERS_BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_start, F.text == "/menu")
    dp.message.register(handle_lang_command, Command("lang"))

    async def chat_lookup(user_id_str: str) -> int | None:
        return await chat_id_for_user_id(user_id_str, role=UserRole.SPECIALIST)

    log.info("DoersBot started")
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
        run_notification_loop(bot, chat_lookup, format_notification, SPECIALIST_NOTIFICATIONS),
    )


if __name__ == "__main__":
    asyncio.run(main())
