"""RefereeBot — anonymous customer↔specialist relay tied to a project."""

from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy import select

from app.core.config import get_settings
from app.core.i18n import DEFAULT as DEFAULT_LANG
from app.core.i18n import normalize
from app.models.application import Application, ApplicationStatus
from app.models.chat import ChatThread
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.services.chat_relay import get_or_open_thread, post_message
from app.services.errors import DomainError
from app.services.projects import select_specialist
from bots.common.auth import get_user_by_tg, update_chat_id
from bots.common.db import SessionLocal
from bots.common.i18n import t
from bots.common.lang import ensure_user_language, language_for_user_id
from bots.common.lang_command import handle_lang_command

settings = get_settings()
log = logging.getLogger("referee_bot")


class ChatState(StatesGroup):
    in_thread = State()


def main_menu_customer(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t("referee.menu.open_projects", lang), callback_data="cust_projects"
            )],
        ]
    )


def main_menu_specialist(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t("referee.menu.active_chats", lang), callback_data="spec_threads"
            )],
        ]
    )


async def _get_user(tg_user_id: int) -> User | None:
    async with SessionLocal() as session:
        return await get_user_by_tg(session, tg_user_id)


async def _lang_for(tg_user_id: int, tg_user=None) -> str:
    """Resolve language for an incoming-message handler.

    Uses the persisted preference when available, else falls back to the
    Telegram-reported language code on this message, else DEFAULT.
    """
    async with SessionLocal() as session:
        user = await get_user_by_tg(session, tg_user_id)
        if user is not None and user.language:
            return normalize(user.language)
    if tg_user is not None:
        return normalize(getattr(tg_user, "language_code", None))
    return DEFAULT_LANG


async def on_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)
        user = await get_user_by_tg(session, message.from_user.id)
        lang = await ensure_user_language(session, user, message.from_user)

    if user is None:
        await message.answer(
            t("referee.welcome_unknown", lang),
            parse_mode="HTML",
        )
        return

    if user.role == UserRole.CUSTOMER:
        await message.answer(
            t("referee.welcome_customer", lang),
            reply_markup=main_menu_customer(lang),
        )
    else:
        await message.answer(
            t("referee.welcome_specialist", lang),
            reply_markup=main_menu_specialist(lang),
        )


async def on_menu(message: Message) -> None:
    lang = await _lang_for(message.from_user.id, message.from_user)
    user = await _get_user(message.from_user.id)
    if user is None:
        await message.answer(t("shared.sign_up_first", lang))
        return
    if user.role == UserRole.CUSTOMER:
        await message.answer(
            t("referee.menu.title_customer", lang),
            reply_markup=main_menu_customer(lang),
        )
    else:
        await message.answer(
            t("referee.menu.title_specialist", lang),
            reply_markup=main_menu_specialist(lang),
        )


# ---------------- Customer: list open projects ----------------

async def cb_customer_projects(call: CallbackQuery) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    async with SessionLocal() as session:
        res = await session.execute(
            select(Project).where(
                Project.customer_id == user.id,
                Project.status == ProjectStatus.OPEN,
            )
        )
        projects = list(res.scalars().all())
    if not projects:
        await call.message.answer(t("referee.empty.open_projects", lang))
        await call.answer()
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p.title, callback_data=f"proj:{p.id}")]
            for p in projects
        ]
    )
    await call.message.answer(t("referee.lists.open_projects", lang), reply_markup=kb)
    await call.answer()


async def cb_project_picked(call: CallbackQuery) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    project_id = UUID(call.data.split(":", 1)[1])
    async with SessionLocal() as session:
        res = await session.execute(
            select(Application).where(
                Application.project_id == project_id,
                Application.status == ApplicationStatus.PENDING,
            )
        )
        apps = list(res.scalars().all())
    if not apps:
        await call.message.answer(t("referee.empty.applicants", lang))
        await call.answer()
        return

    rows = []
    for idx, a in enumerate(apps, start=1):
        rows.append([
            InlineKeyboardButton(
                text=t("referee.chat.row_chat", lang, idx=idx),
                callback_data=f"chat:{project_id}:{a.specialist_id}",
            ),
            InlineKeyboardButton(
                text=t("referee.chat.row_select", lang, idx=idx),
                callback_data=f"select:{project_id}:{a.specialist_id}",
            ),
        ])
    await call.message.answer(
        t("referee.lists.applicants", lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await call.answer()


async def cb_open_chat(call: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    _, project_id_str, specialist_id_str = call.data.split(":")
    project_id = UUID(project_id_str)
    specialist_id = UUID(specialist_id_str)

    async with SessionLocal() as session:
        try:
            thread = await get_or_open_thread(session, project_id, user.id, specialist_id)
        except DomainError as e:
            await call.answer(e.message, show_alert=True)
            return

    await state.set_state(ChatState.in_thread)
    await state.update_data(thread_id=str(thread.id))
    await call.message.answer(t("referee.chat.entered_customer", lang))
    await call.answer()


async def cb_select(call: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    _, project_id_str, specialist_id_str = call.data.split(":")
    async with SessionLocal() as session:
        try:
            project = await select_specialist(
                session, user, UUID(project_id_str), UUID(specialist_id_str)
            )
        except DomainError as e:
            await call.answer(e.message, show_alert=True)
            return
    await call.message.answer(
        t("referee.chat.selected", lang, title=project.title), parse_mode="HTML"
    )
    await state.clear()
    await call.answer()


# ---------------- Specialist: list active chats ----------------

async def cb_specialist_threads(call: CallbackQuery) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.SPECIALIST:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    async with SessionLocal() as session:
        res = await session.execute(
            select(ChatThread, Project)
            .join(Project, Project.id == ChatThread.project_id)
            .where(ChatThread.specialist_id == user.id, ChatThread.closed.is_(False))
        )
        threads = res.all()
    if not threads:
        await call.message.answer(t("referee.empty.active_chats", lang))
        await call.answer()
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p.title, callback_data=f"open_thread:{t_.id}")]
            for t_, p in threads
        ]
    )
    await call.message.answer(t("referee.lists.pick_chat", lang), reply_markup=kb)
    await call.answer()


async def cb_open_thread(call: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(call.from_user.id, call.from_user)
    user = await _get_user(call.from_user.id)
    if user is None:
        await call.answer(t("shared.not_allowed", lang), show_alert=True)
        return
    thread_id_str = call.data.split(":", 1)[1]
    await state.set_state(ChatState.in_thread)
    await state.update_data(thread_id=thread_id_str)
    await call.message.answer(t("referee.chat.entered_specialist", lang))
    await call.answer()


async def on_leave(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id, message.from_user)
    await state.clear()
    await message.answer(t("referee.chat.left", lang))


# ---------------- Relay incoming messages ----------------

async def on_text_in_thread(message: Message, state: FSMContext, bot: Bot) -> None:
    sender_lang = await _lang_for(message.from_user.id, message.from_user)
    data = await state.get_data()
    thread_id_str = data.get("thread_id")
    if not thread_id_str:
        return
    thread_id = UUID(thread_id_str)
    user = await _get_user(message.from_user.id)
    if user is None:
        await state.clear()
        return

    async with SessionLocal() as session:
        try:
            _msg, _thread, party, counterparty_id = await post_message(
                session, thread_id, user, message.text or "", tg_message_id=message.message_id
            )
        except DomainError as e:
            await message.answer(t("shared.error_prefix", sender_lang, message=e.message))
            return

        # find counterparty chat_id + language
        from app.models.telegram import TelegramAccount

        res = await session.execute(
            select(TelegramAccount.chat_id).where(TelegramAccount.user_id == counterparty_id)
        )
        chat_id = res.scalar_one_or_none()
        recipient_lang = await language_for_user_id(session, counterparty_id)

    if chat_id:
        label_key = (
            "referee.chat.label_customer"
            if party.value == "customer"
            else "referee.chat.label_specialist"
        )
        label = t(label_key, recipient_lang)
        try:
            await bot.send_message(
                chat_id, f"<b>{label}:</b> {message.text}", parse_mode="HTML"
            )
        except Exception:
            log.exception("Failed to forward message to %s", chat_id)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    if not settings.TG_REFEREE_BOT_TOKEN:
        log.error("TG_REFEREE_BOT_TOKEN not set — exiting")
        return
    bot = Bot(settings.TG_REFEREE_BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(on_start, CommandStart())
    dp.message.register(on_menu, Command("menu"))
    dp.message.register(on_leave, Command("leave"))
    dp.message.register(handle_lang_command, Command("lang"))
    dp.callback_query.register(cb_customer_projects, F.data == "cust_projects")
    dp.callback_query.register(cb_specialist_threads, F.data == "spec_threads")
    dp.callback_query.register(cb_project_picked, F.data.startswith("proj:"))
    dp.callback_query.register(cb_open_chat, F.data.startswith("chat:"))
    dp.callback_query.register(cb_select, F.data.startswith("select:"))
    dp.callback_query.register(cb_open_thread, F.data.startswith("open_thread:"))

    # Free-form text only while inside a thread
    dp.message.register(on_text_in_thread, ChatState.in_thread, F.text & ~F.text.startswith("/"))

    log.info("RefereeBot started")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
