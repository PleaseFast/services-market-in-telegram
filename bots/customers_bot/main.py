"""DoingsForCustomersBot — customer assistant + Mini App entry + notifications."""

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
log = logging.getLogger("customers_bot")


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t("shared.open_app", lang),
                web_app=WebAppInfo(url=f"{settings.TG_WEBAPP_URL}/?role=customer"),
            )],
            [InlineKeyboardButton(
                text=t("customers.menu.my_projects", lang), callback_data="my_projects"
            )],
            [InlineKeyboardButton(
                text=t("customers.menu.drafts", lang), callback_data="drafts"
            )],
        ]
    )


async def on_start(message: Message) -> None:
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)
        user = await get_user_by_tg(session, message.from_user.id)
        lang = await ensure_user_language(session, user, message.from_user)
    await message.answer(
        t("customers.welcome", lang),
        parse_mode="HTML",
        reply_markup=main_menu(lang),
    )


CUSTOMER_NOTIFICATIONS = {
    "new_application",
    "specialist_selected",
    "direct_offer_answered",
    "new_review",
}


def format_notification(payload: dict, lang: str = DEFAULT_LANG) -> str:
    notif_type = payload.get("type", "")
    p = payload.get("payload", {})
    title = p.get("title") or t("notifications.fallback_title", lang)
    if notif_type == "new_application":
        return t("notifications.new_application", lang, title=title)
    if notif_type == "specialist_selected":
        return t("notifications.specialist_selected", lang, title=title)
    if notif_type == "direct_offer_answered":
        key = (
            "notifications.direct_offer_answered_accepted"
            if p.get("accepted")
            else "notifications.direct_offer_answered_declined"
        )
        return t(key, lang)
    if notif_type == "new_review":
        return t("notifications.new_review_customer", lang, rating=p.get("rating", "?"))
    return t("notifications.fallback", lang, type=notif_type)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not settings.TG_CUSTOMERS_BOT_TOKEN:
        log.error("TG_CUSTOMERS_BOT_TOKEN not set — exiting")
        return
    bot = Bot(settings.TG_CUSTOMERS_BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_start, F.text == "/menu")
    dp.message.register(handle_lang_command, Command("lang"))

    async def chat_lookup(user_id_str: str) -> int | None:
        return await chat_id_for_user_id(user_id_str, role=UserRole.CUSTOMER)

    log.info("CustomersBot started")
    await asyncio.gather(
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
        run_notification_loop(bot, chat_lookup, format_notification, CUSTOMER_NOTIFICATIONS),
    )


if __name__ == "__main__":
    asyncio.run(main())
