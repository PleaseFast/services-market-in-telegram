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
from app.models.application import Application, ApplicationStatus
from app.models.chat import ChatThread
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.services.chat_relay import get_or_open_thread, post_message
from app.services.errors import DomainError
from app.services.projects import select_specialist
from bots.common.auth import update_chat_id
from bots.common.db import SessionLocal

settings = get_settings()
log = logging.getLogger("referee_bot")


class ChatState(StatesGroup):
    in_thread = State()


def main_menu_customer() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 My open projects", callback_data="cust_projects")],
        ]
    )


def main_menu_specialist() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 My active chats", callback_data="spec_threads")],
        ]
    )


async def _get_user(tg_user_id: int) -> User | None:
    async with SessionLocal() as session:
        from bots.common.auth import get_user_by_tg

        return await get_user_by_tg(session, tg_user_id)


async def on_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with SessionLocal() as session:
        await update_chat_id(session, message.from_user.id, message.chat.id)

    user = await _get_user(message.from_user.id)
    if user is None:
        await message.answer(
            "👋 Welcome to <b>RefereeBot</b>!\n\n"
            "I relay anonymous chats between customers and specialists.\n\n"
            "First, sign up on the web app, then link your Telegram account from the Mini App.",
            parse_mode="HTML",
        )
        return

    if user.role == UserRole.CUSTOMER:
        await message.answer(
            "👋 Welcome back. Pick a project to talk to applicants anonymously.",
            reply_markup=main_menu_customer(),
        )
    else:
        await message.answer(
            "👋 Welcome back. Use /menu to see active chats with customers.",
            reply_markup=main_menu_specialist(),
        )


async def on_menu(message: Message) -> None:
    user = await _get_user(message.from_user.id)
    if user is None:
        await message.answer("Sign up on the web app first.")
        return
    if user.role == UserRole.CUSTOMER:
        await message.answer("Customer menu", reply_markup=main_menu_customer())
    else:
        await message.answer("Specialist menu", reply_markup=main_menu_specialist())


# ---------------- Customer: list open projects ----------------

async def cb_customer_projects(call: CallbackQuery) -> None:
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer("Not allowed", show_alert=True)
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
        await call.message.answer("No open projects.")
        await call.answer()
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p.title, callback_data=f"proj:{p.id}")]
            for p in projects
        ]
    )
    await call.message.answer("Your open projects:", reply_markup=kb)
    await call.answer()


async def cb_project_picked(call: CallbackQuery) -> None:
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer("Not allowed", show_alert=True)
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
        await call.message.answer("No applicants yet.")
        await call.answer()
        return

    rows = []
    for idx, a in enumerate(apps, start=1):
        rows.append([
            InlineKeyboardButton(
                text=f"💬 Chat #{idx}",
                callback_data=f"chat:{project_id}:{a.specialist_id}",
            ),
            InlineKeyboardButton(
                text=f"✅ Select #{idx}",
                callback_data=f"select:{project_id}:{a.specialist_id}",
            ),
        ])
    await call.message.answer(
        "Anonymous applicants for this project:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
    )
    await call.answer()


async def cb_open_chat(call: CallbackQuery, state: FSMContext) -> None:
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer("Not allowed", show_alert=True)
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
    await call.message.answer(
        "💬 You're now in an anonymous chat with this specialist.\n"
        "Type messages here; they'll be forwarded. Use /leave to exit.",
    )
    await call.answer()


async def cb_select(call: CallbackQuery, state: FSMContext) -> None:
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.CUSTOMER:
        await call.answer("Not allowed", show_alert=True)
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
    await call.message.answer(f"✅ Selected for <b>{project.title}</b>.", parse_mode="HTML")
    await state.clear()
    await call.answer()


# ---------------- Specialist: list active chats ----------------

async def cb_specialist_threads(call: CallbackQuery) -> None:
    user = await _get_user(call.from_user.id)
    if user is None or user.role != UserRole.SPECIALIST:
        await call.answer("Not allowed", show_alert=True)
        return
    async with SessionLocal() as session:
        res = await session.execute(
            select(ChatThread, Project)
            .join(Project, Project.id == ChatThread.project_id)
            .where(ChatThread.specialist_id == user.id, ChatThread.closed.is_(False))
        )
        threads = res.all()
    if not threads:
        await call.message.answer("No active chats.")
        await call.answer()
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p.title, callback_data=f"open_thread:{t.id}")]
            for t, p in threads
        ]
    )
    await call.message.answer("Pick a chat to enter:", reply_markup=kb)
    await call.answer()


async def cb_open_thread(call: CallbackQuery, state: FSMContext) -> None:
    user = await _get_user(call.from_user.id)
    if user is None:
        await call.answer("Not allowed", show_alert=True)
        return
    thread_id_str = call.data.split(":", 1)[1]
    await state.set_state(ChatState.in_thread)
    await state.update_data(thread_id=thread_id_str)
    await call.message.answer("💬 Entered chat. Type messages here; /leave to exit.")
    await call.answer()


async def on_leave(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Left the chat.")


# ---------------- Relay incoming messages ----------------

async def on_text_in_thread(message: Message, state: FSMContext, bot: Bot) -> None:
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
            await message.answer(f"⚠️ {e.message}")
            return

        # find counterparty chat_id
        from app.models.telegram import TelegramAccount

        res = await session.execute(
            select(TelegramAccount.chat_id).where(TelegramAccount.user_id == counterparty_id)
        )
        chat_id = res.scalar_one_or_none()

    if chat_id:
        label = "Customer" if party.value == "customer" else "Specialist"
        try:
            await bot.send_message(chat_id, f"<b>{label}:</b> {message.text}", parse_mode="HTML")
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
