import json
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from Patterns.PatternManager import PatternManager
from Patterns.TableRenderer import TableRenderer
from config import BOT_TOKEN, ADMIN_CHAT_ID, MY_TG_ID
from database import Database
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)
db = Database()

# States
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_new_name = State()
    waiting_for_fake_name = State()
    waiting_for_name_to_delete = State()
    waiting_for_user_to_remove = State()
    waiting_for_user_to_rename = State()
    waiting_pattern_selection = State()
    waiting_pattern_add = State()

# Inline keyboards
def get_registration_keyboard(request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{request_id}"),
            InlineKeyboardButton(text="❌ Запретить", callback_data=f"reject_{request_id}")
        ]
    ])

def get_role_keyboard(request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👑 Лидер", callback_data=f"role_leader_{request_id}"),
            InlineKeyboardButton(text="⚔️ Солдат", callback_data=f"role_soldier_{request_id}")
        ],
        [
            InlineKeyboardButton(text="👤 Участник", callback_data=f"role_member_{request_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"role_reject_{request_id}")
        ]
    ])

def get_main_menu_keyboard(is_admin: bool = False, is_god: bool = False):
    keyboard = [
        [InlineKeyboardButton(text="✏️ Поменять имя", callback_data="change_name")],
        [InlineKeyboardButton(text="📈 Запросить повышение", callback_data="request_promotion")],
        [InlineKeyboardButton(text="🚪 Уйти", callback_data="leave")]
    ]
    
    if is_admin or is_god:
        keyboard.extend([
            [InlineKeyboardButton(text="👤 Поменять имя другому", callback_data="change_other_name")],
            [InlineKeyboardButton(text="🗑️ Удалить другого", callback_data="remove_other")],
            [InlineKeyboardButton(text="➕ Добавить фиктивное имя", callback_data="add_fake_name")],
            [InlineKeyboardButton(text="➖ Удалить фиктивное имя", callback_data="delete_fake_name")],
            [InlineKeyboardButton(text="📊 Посмотреть таблицу", callback_data="view_table")]
        ])
        
    if is_god:
        keyboard.extend([
            [InlineKeyboardButton(text="📄 Задать паттерн", callback_data="add_pattern")],
            [InlineKeyboardButton(text="📑 Поменять паттерн", callback_data="set_pattern")],
        ])

    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)





def get_self_role_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👑 Лидер", callback_data="self_role_leader"),
            InlineKeyboardButton(text="⚔️ Солдат", callback_data="self_role_soldier")
        ],
        [
            InlineKeyboardButton(text="👤 Участник", callback_data="self_role_member"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ]
    ])

async def get_user_with_admin_check(tg_id: int):
    """Получить данные пользователя с проверкой админских прав"""
    user = await db.get_user(tg_id)
    is_admin = await db.is_admin(tg_id)
    return user, is_admin

# Start command
@router.message(Command("start"))
async def cmd_start(message: Message):
    user, is_admin = await get_user_with_admin_check(message.from_user.id)
    
    if not user:
        # New user - show registration
        await message.answer(
            "Добро пожаловать! Для доступа к функционалу бота необходимо зарегистрироваться.\n"
            "Используйте команду /register для подачи заявки."
        )
    else:
        if user["status"] == "approved":
            # Approved user
            await message.answer(
                f"Добро пожаловать, {user['username']}!\n"
                f"Ваш текущий ник: {user['player_name']}\n"
                f"Ваша роль: {user['role']}\n"
                f"{'👑 Вы администратор' if is_admin else ''}",
                reply_markup=get_main_menu_keyboard(is_admin,message.from_user.id == int(MY_TG_ID))
            )
        else:
            # Pending user
            await message.answer(
                "Ваша заявка находится на рассмотрении. Ожидайте подтверждения от администратора."
            )

# Help command
@router.message(Command("help"))
async def cmd_help(message: Message):
    user, is_admin = await get_user_with_admin_check(message.from_user.id)
    
    if user and user["status"] == "approved":
        help_text = (
            "📋 Доступные команды:\n\n"
            "✏️ Поменять имя - изменить ваш игровой ник\n"
            "📈 Запросить повышение - запросить изменение роли\n"
            "🚪 Уйти - покинуть альянс\n\n"
        )
        
        if is_admin:
            help_text += (
                "👤 Поменять имя другому - изменить ник другого участника\n"
                "🗑️ Удалить другого - удалить участника из альянса\n"
                "➕ Добавить фиктивное имя - добавить имя без Telegram\n"
                "➖ Удалить фиктивное имя - удалить фиктивное имя\n"
                "📊 Посмотреть таблицу - получить Excel таблицу\n"
            )
        if message.from_user.id == int(MY_TG_ID):
                        help_text += (
                "📄 Задать паттерн - задает паттерн строительства таблицы\n"
                "📑 Поменять паттерн - выбирает паттерн среди существующих\n"
                "Также доступны команды:\n"
                "/list_chats - список чатов в которых действует система NICK\n"
                "/add_chat - команда для добавления системы NICK в текущий чат\n"
                "/remove_chat - команда для удаления системы NICK из текущего чата\n"
                "/grant_admin <id> - выдает права администратора бота для пользователя с заданным id\n"
            )
        
        await message.answer(help_text, reply_markup=get_main_menu_keyboard(is_admin,message.from_user.id == int(MY_TG_ID)))
    else:
        await message.answer("Для доступа к функциям бота необходимо зарегистрироваться. Используйте /register")

# Register command
@router.message(Command("register"))
async def cmd_register(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    tag = f"@{username}" if username else f"id{user_id}"
    
    # Check if already registered
    existing_user = await db.get_user(user_id)
    if existing_user:
        if existing_user["status"] == "pending":
            await message.answer("Ваша заявка уже находится на рассмотрении.")
        else:
            await message.answer("Вы уже зарегистрированы!")
        return
    
    # Add to database with pending status
    if await db.add_user(user_id, username, tag, "pending"):
        # Send request to admin chat
        request_text = (
            f"🆕 Новая заявка на регистрацию:\n\n"
            f"👤 Пользователь: {username}\n"
            f"🏷️ Тег: {tag}\n"
            f"🆔 TG ID: {user_id}\n\n"
            f"Запрашивает разрешение на запись в таблицу Dice."
        )
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            request_text,
            reply_markup=get_registration_keyboard(user_id)
        )
        
        await message.answer("✅ Заявка отправлена на рассмотрение! Ожидайте подтверждения от администратора.")
    else:
        await message.answer("❌ Произошла ошибка при отправке заявки. Попробуйте позже.")

# Registration approval callbacks
@router.callback_query(F.data.startswith("approve_"))
async def approve_registration(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    
    # Update user status
    if await db.update_user_status(user_id, "approved"):
        # Notify user
        await bot.send_message(user_id, "✅ Ваша заявка одобрена! Теперь у вас есть доступ к функции бота.")
        
        # Update admin message
        await callback.message.edit_text(
            f"✅ {callback.from_user.username} одобрил заявку пользователя {user_id}",
            reply_markup=None
        )
        await callback.answer("Заявка одобрена!")
    else:
        await callback.answer("Ошибка при одобрении заявки!", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def reject_registration(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[1])
    
    # Delete user
    if await db.delete_user(user_id):
        # Notify user
        await bot.send_message(user_id, "❌ Ваша заявка отклонена администратором.")
        
        # Update admin message
        await callback.message.edit_text(
            f"❌ {callback.from_user.username} отклонил заявку пользователя {user_id}",
            reply_markup=None
        )
        await callback.answer("Заявка отклонена!")
    else:
        await callback.answer("Ошибка при отклонении заявки!", show_alert=True)

# Change name
@router.callback_query(F.data == "change_name")
async def change_name_start(callback: CallbackQuery, state: FSMContext):
    user, is_admin = await get_user_with_admin_check(callback.from_user.id)
    if not user or user["status"] != "approved":
        await callback.answer("У вас нет доступа к этой функции!", show_alert=True)
        return
    
    await callback.message.answer("Введите новый игровой ник:")
    await state.set_state(RegistrationStates.waiting_for_new_name)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_new_name)
async def change_name_finish(message: Message, state: FSMContext):
    new_name = message.text.strip()
    
    if await db.update_user_name(message.from_user.id, new_name):
        await message.answer(f"✅ Ваш ник успешно изменен на: {new_name}")
    else:
        await message.answer("❌ Произошла ошибка при изменении ника. Попробуйте позже.")
    
    await state.clear()

# Request promotion
@router.callback_query(F.data == "request_promotion")
async def request_promotion(callback: CallbackQuery):
    user, is_admin = await get_user_with_admin_check(callback.from_user.id)
    if not user or user["status"] != "approved":
        await callback.answer("У вас нет доступа к этой функции!", show_alert=True)
        return
    
    # Если пользователь админ - он может сразу менять себе роль
    if is_admin:
        await callback.message.answer(
            "Выберите новую роль для себя:",
            reply_markup=get_self_role_keyboard()
        )
    else:
        # Обычные пользователи отправляют запрос админам
        request_text = (
            f"📈 Запрос на изменение роли:\n\n"
            f"👤 Пользователь: {user['username']}\n"
            f"🏷️ Тег: {user['tag']}\n"
            f"🆔 TG ID: {user['tg_id']}\n"
            f"📊 Текущая роль: {user['role']}\n\n"
            f"Запрашивает изменение роли."
        )
        
        await bot.send_message(
            ADMIN_CHAT_ID,
            request_text,
            reply_markup=get_role_keyboard(user['tg_id'])
        )
        
        await callback.message.answer("✅ Запрос на изменение роли отправлен администраторам!")
    await callback.answer()

# Role change callbacks
@router.callback_query(F.data.startswith("role_"))
async def handle_role_change(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    data_parts = callback.data.split("_")
    action = data_parts[1]
    user_id = int(data_parts[2])
    
    if action == "reject":
        await callback.message.edit_text(
            f"❌ {callback.from_user.username} отклонил запрос на изменение роли",
            reply_markup=None
        )
        await callback.answer("Запрос отклонен!")
        return
    
    role_map = {
        "leader": "лидер",
        "soldier": "солдат", 
        "member": "участник"
    }
    
    new_role = role_map.get(action)
    if new_role and await db.update_user_role(user_id, new_role):
        # Notify user
        await bot.send_message(user_id, f"✅ Ваша роль изменена на: {new_role}")
        
        # Update admin message
        await callback.message.edit_text(
            f"✅ {callback.from_user.username} изменил роль пользователя на: {new_role}",
            reply_markup=None
        )
        await callback.answer("Роль изменена!")
    else:
        await callback.answer("Ошибка при изменении роли!", show_alert=True)

# Self role change for admins
@router.callback_query(F.data.startswith("self_role_"))
async def handle_self_role_change(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    role_map = {
        "self_role_leader": "лидер",
        "self_role_soldier": "солдат", 
        "self_role_member": "участник"
    }
    
    new_role = role_map.get(callback.data)
    if new_role and await db.update_user_role(callback.from_user.id, new_role):
        await callback.message.answer(f"✅ Ваша роль изменена на: {new_role}")
        await callback.answer()
    else:
        await callback.answer("❌ Ошибка при изменении роли!", show_alert=True)

# Leave alliance
@router.callback_query(F.data == "leave")
async def leave_alliance(callback: CallbackQuery):
    user, is_admin = await get_user_with_admin_check(callback.from_user.id)
    if not user or user["status"] != "approved":
        await callback.answer("У вас нет доступа к этой функции!", show_alert=True)
        return
    
    if await db.delete_user(callback.from_user.id):
        await callback.message.answer("🚪 Вы покинули альянс. Для повторного доступа необходимо зарегистрироваться.")
        await callback.answer()
    else:
        await callback.answer("❌ Произошла ошибка при выходе из альянса!", show_alert=True)

# Admin commands
@router.callback_query(F.data == "change_other_name")
async def change_other_name_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    await callback.message.answer("Введите TG ID пользователя и новый ник в формате:\n`123456789 НовыйНик`")
    await state.set_state(RegistrationStates.waiting_for_user_to_rename)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_user_to_rename)
async def change_other_name_finish(message: Message, state: FSMContext):
    try:
        parts = message.text.strip().split(' ', 1)
        if len(parts) != 2:
            await message.answer("❌ Неверный формат. Используйте: `123456789 НовыйНик`")
            return
        
        user_id = int(parts[0])
        new_name = parts[1]
        
        # Check if target is admin
        if await db.is_admin(user_id):
            await message.answer("❌ Нельзя изменять ники администраторов!")
            return
        
        if await db.update_user_name(user_id, new_name):
            await message.answer(f"✅ Ник пользователя {user_id} изменен на: {new_name}")
            # Notify user
            await bot.send_message(user_id, f"✅ Администратор изменил ваш ник на: {new_name}")
        else:
            await message.answer("❌ Пользователь не найден или произошла ошибка!")
    
    except ValueError:
        await message.answer("❌ Неверный формат ID. Используйте числовой ID.")
    
    await state.clear()

@router.callback_query(F.data == "remove_other")
async def remove_other_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    await callback.message.answer("Введите игровое имя пользователя для удаления:")
    await state.set_state(RegistrationStates.waiting_for_user_to_remove)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_user_to_remove)
async def remove_other_finish(message: Message, state: FSMContext):
    try:
        user_player_name = message.text.strip()
        user_id = 0
        user = await db.get_user_by_player_name(user_player_name)
        if user:
            user_id = user['tg_id']

        # Check if target is admin
        if await db.is_admin(user_id):
            await message.answer("❌ Нельзя удалять администраторов!")
            return
        
        if await db.delete_user(user_id):
            await message.answer(f"✅ Пользователь {user_id} удален из альянса.")
            # Notify user
            await bot.send_message(user_id, "🚪 Администратор удалил вас из альянса.")
        else:
            await message.answer("❌ Пользователь не найден или произошла ошибка!")
    
    except ValueError:
        await message.answer("❌ Неверный формат ID. Используйте числовой ID.")
    
    await state.clear()

# В обработчике добавления фиктивного имени
@router.callback_query(F.data == "add_fake_name")
async def add_fake_name_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    await callback.message.answer(
        "Введите фиктивное имя для добавления и роль через пробел:\n"
        "Например: `Игрок123 участник`\n"
        "Доступные роли: участник, солдат, лидер"
    )
    await state.set_state(RegistrationStates.waiting_for_fake_name)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_fake_name)
async def add_fake_name_finish(message: Message, state: FSMContext):
    try:
        parts = message.text.strip().split(' ', 1)
        if len(parts) == 1:
            # Только имя, используем роль по умолчанию
            player_name = parts[0]
            role = "участник"
        else:
            player_name = parts[0]
            role = parts[1].lower()
        
        # Проверяем валидность роли
        valid_roles = ["участник", "солдат", "лидер"]
        if role not in valid_roles:
            await message.answer("❌ Неверная роль! Используйте: участник, солдат или лидер")
            return
        
        if await db.add_fake_name(player_name, role):
            await message.answer(f"✅ Фиктивный игрок '{player_name}' добавлен с ролью '{role}'!")
        else:
            await message.answer("❌ Произошла ошибка при добавлении игрока!")
    
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    
    await state.clear()

# В обработчике удаления фиктивного имени
@router.callback_query(F.data == "delete_fake_name")
async def delete_fake_name_start(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    # Показываем список фиктивных игроков для удаления
    fake_names = await db.get_all_fake_names()
    if not fake_names:
        await callback.message.answer("❌ Нет фиктивных игроков для удаления!")
        return
    
    keyboard = []
    for fake in fake_names:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ {fake['player_name']} ({fake['role']})",
                callback_data=f"delete_fake_{fake['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    
    await callback.message.answer(
        "Выберите фиктивного игрока для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delete_fake_"))
async def delete_fake_name_handler(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    fake_id = int(callback.data.split("_")[2])
    
    if await db.delete_fake_name(fake_id):
        await callback.message.edit_text("✅ Фиктивный игрок удален!")
        await callback.answer()
    else:
        await callback.answer("❌ Ошибка при удалении игрока!", show_alert=True)

# Обновляем обработчик просмотра таблицы
@router.callback_query(F.data == "view_table")
async def view_table(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия!", show_alert=True)
        return
    
    # Получаем все массивы игроков
    all_players = await db.get_all_players()
    recent_players = await db.get_recent_players()
    leaders = await db.get_leaders()
    soldiers = await db.get_soldiers()
    regular_members = await db.get_regular_members()
    
    # Формируем статистику
    summary = (
        f"📊 Полная статистика альянса:\n\n"
        f"👥 Всего игроков: {len(all_players)}\n"
        f"📱 Telegram игроков: {len([p for p in all_players if p['player_type'] == 'telegram'])}\n"
        f"👤 Фиктивных игроков: {len([p for p in all_players if p['player_type'] == 'fake'])}\n"
        f"👑 Лидеров: {len(leaders)}\n"
        f"⚔️ Солдат: {len(soldiers)}\n"
        f"👤 Участников: {len(regular_members)}\n"
        f"✏️ Изменилось за 24ч: {len(recent_players)}\n\n"
    )
    
    # Детальная информация по лидерам
    if leaders:
        summary += "👑 Лидеры:\n"
        for player in leaders:
            emoji = "🤖" if player['player_type'] == 'fake' else "👤"
            summary += f"{emoji} {player['player_name']}\n"
        summary += "\n"
    
    # Детальная информация по солдатам
    if soldiers:
        summary += "⚔️ Солдаты:\n"
        for player in soldiers:
            emoji = "🤖" if player['player_type'] == 'fake' else "👤"
            summary += f"{emoji} {player['player_name']}\n"
        summary += "\n"
    
    # Недавние изменения
    if recent_players:
        summary += "✏️ Недавно изменены:\n"
        for player in recent_players:
            emoji = "🤖" if player['player_type'] == 'fake' else "👤"
            role_emoji = "👑" if player['role'] == 'лидер' else "⚔️" if player['role'] == 'солдат' else "👤"
            summary += f"{emoji} {role_emoji} {player['player_name']}\n"
    
    
    
    pattern_manager = PatternManager(db)
    pattern = await pattern_manager.get_active_pattern()
    
    if not pattern:
        await callback.message.answer("Нет активного паттерна. Сначала создайте паттерн.")
        return
    
    # Получаем данные игроков     
    users_response = await db.get_all_players()
    # Здесь нужно получить списки лидеров, солдат и обновивших
    # (замените на вашу логику получения этих списков)
    leaders = await db.get_leaders()  # Ваша логика для лидеров
    soldiers = await db.get_soldiers()  # Ваша логика для солдат
    updated_players = await db.get_recent_players()  # Игроки, обновившие имя за последние N дней
    
    renderer = TableRenderer()
    grouped_players = renderer.group_players_by_pattern(users_response, pattern)
    
    # Создаем изображение
    image_buf = renderer.create_table_image(pattern, grouped_players, leaders, soldiers, updated_players)
    
    
    await callback.message.answer_photo(InputFile(image_buf, filename='player_table.png'),caption=summary)
    await callback.answer("Статистика сформирована!")
# Cancel handler
@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено.")
    await callback.answer()

# Grant admin command (only for you)
@router.message(Command("grant_admin"))
async def cmd_grant_admin(message: Message):
    if message.from_user.id != int(MY_TG_ID):
        await message.answer("❌ У вас нет прав для этой команды!")
        return
    
    try:
        # Extract user ID from command: /grant_admin 123456789
        target_id = int(message.text.split()[1])
        target_user = await bot.get_chat(target_id)
        
        if await db.add_admin(target_id, target_user.username or "Без имени"):
            await message.answer(f"✅ Пользователь {target_user.username} назначен администратором!")
            await bot.send_message(target_id, "🎉 Вы были назначены администратором бота! Теперь вы можете управлять своими данными напрямую.")
        else:
            await message.answer("❌ Ошибка при назначении администратора!")
    
    except (IndexError, ValueError):
        await message.answer("❌ Используйте: /grant_admin <user_id>")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        

# Команды управления разрешенными чатами (только для владельца)
@router.message(Command("add_chat"))
async def cmd_add_chat(message: Message):
    """Добавить текущий чат в разрешенные"""
    if message.from_user.id != int(MY_TG_ID):
        await message.answer("❌ У вас нет прав для этой команды!")
        return
    
    chat_id = message.chat.id
    chat_title = message.chat.title or "Личные сообщения"
    
    if await db.is_chat_allowed(chat_id):
        await message.answer("✅ Этот чат уже в списке разрешенных!")
        return
    
    if await db.add_allowed_chat(chat_id, chat_title):
        await message.answer(f"✅ Чат '{chat_title}' добавлен в разрешенные!")
    else:
        await message.answer("❌ Ошибка при добавлении чата!")

@router.message(Command("remove_chat"))
async def cmd_remove_chat(message: Message):
    """Удалить текущий чат из разрешенных"""
    if message.from_user.id != int(MY_TG_ID):
        await message.answer("❌ У вас нет прав для этой команды!")
        return
    
    chat_id = message.chat.id
    chat_title = message.chat.title or "Личные сообщения"
    
    if not await db.is_chat_allowed(chat_id):
        await message.answer("❌ Этот чат не в списке разрешенных!")
        return
    
    if await db.remove_allowed_chat(chat_id):
        await message.answer(f"✅ Чат '{chat_title}' удален из разрешенных!")
    else:
        await message.answer("❌ Ошибка при удалении чата!")

@router.message(Command("list_chats"))
async def cmd_list_chats(message: Message):
    """Показать список разрешенных чатов"""
    if message.from_user.id != int(MY_TG_ID):
        await message.answer("❌ У вас нет прав для этой команды!")
        return
    
    allowed_chats = await db.get_all_allowed_chats()
    if not allowed_chats:
        await message.answer("📝 Нет разрешенных чатов.")
        return
    
    chat_list = "📝 Разрешенные чаты:\n\n"
    for chat in allowed_chats:
        chat_list += f"• ID: {chat['chat_id']}\n"
        chat_list += f"  Название: {chat['chat_title']}\n"
        chat_list += f"  Добавлен: {chat['created_at'][:10]}\n\n"
    
    await message.answer(chat_list)
    

# Хендлер для +NICK <Свое имя>
@router.message(F.text.startswith("+NICK "))
async def handle_plus_nick(message: Message):
    # Проверяем, что это разрешенный чат
    if not await db.is_chat_allowed(message.chat.id):
        return
    
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    tag = f"@{username}" if username else f"id{user_id}"
    
    # Извлекаем имя из сообщения
    try:
        player_name = message.text[6:].strip()  # Убираем "+NICK "
        if not player_name:
            await message.reply("❌ Укажите имя после +NICK")
            return
    except:
        await message.reply("❌ Неверный формат. Используйте: +NICK ВашеИмя")
        return
    
    # Проверяем существующего пользователя
    existing_user = await db.get_user(user_id)
    
    if existing_user:
        # Пользователь существует - обновляем имя
        if await db.update_user_name(user_id, player_name):
            await message.reply(f"✅ Ваш ник обновлен на: {player_name}")
            # Отправляем уведомление в личные сообщения
            try:
                await bot.send_message(
                    user_id,
                    f"✅ Ваш ник успешно обновлен на: {player_name}\n"
                )
            except:
                pass  # Если бот не может написать в ЛС
        else:
            await message.reply("❌ Ошибка при обновлении ника")
    else:
        # Новый пользователь - регистрируем без подтверждения
        if await db.add_user(user_id, username, tag, "approved"):
            # Сразу обновляем имя
            await db.update_user_name(user_id, player_name)
            
            await message.reply(f"✅ Вы зарегистрированы с ником: {player_name}")
            # Отправляем уведомление в личные сообщения
            try:
                await bot.send_message(
                    user_id,
                    f"🎉 Добро пожаловать в альянс Dice!\n"
                    f"✅ Вы успешно зарегистрированы с ником: {player_name}\n\n"
                    f"Теперь вам доступен полный функционал бота!\n"
                    f"Используйте команду /start для просмотра доступных функций."
                )
            except:
                pass  # Если бот не может написать в ЛС
        else:
            await message.reply("❌ Ошибка при регистрации")

# Хендлер для !NICK <Его имя> (ответ на сообщение)
@router.message(F.text.startswith("!NICK "))
async def handle_exclamation_nick(message: Message):
    # Проверяем, что это разрешенный чат
    if not await db.is_chat_allowed(message.chat.id):
        return
    
    # Проверяем, что отправитель - админ
    if not await db.is_admin(message.from_user.id):
        return
    
    # Проверяем, что это ответ на сообщение
    if not message.reply_to_message:
        await message.reply("❌ Эта команда должна быть ответом на сообщение пользователя!")
        return
    
    target_user = message.reply_to_message.from_user
    target_id = target_user.id
    target_username = target_user.username or "Без имени"
    target_tag = f"@{target_username}" if target_username else f"id{target_id}"
    
    # Извлекаем имя из сообщения
    try:
        player_name = message.text[6:].strip()  # Убираем "!NICK "
        if not player_name:
            await message.reply("❌ Укажите имя после !NICK")
            return
    except:
        await message.reply("❌ Неверный формат. Используйте: !NICK ИмяИгрока")
        return
    
    # Проверяем существующего пользователя
    existing_user = await db.get_user(target_id)
    
    if existing_user:
        # Пользователь существует - обновляем имя
        if await db.update_user_name(target_id, player_name):
            await message.reply(f"✅ Ник пользователя обновлен на: {player_name}")
            # Уведомляем пользователя
            try:
                await bot.send_message(
                    target_id,
                    f"✅ Администратор изменил ваш ник на: {player_name}"
                )
            except:
                pass
        else:
            await message.reply("❌ Ошибка при обновлении ника")
    else:
        # Новый пользователь - регистрируем
        if await db.add_user(target_id, target_username, target_tag, "approved"):
            # Сразу обновляем имя
            await db.update_user_name(target_id, player_name)
            
            await message.reply(f"✅ Пользователь зарегистрирован с ником: {player_name}")
            # Уведомляем пользователя
            try:
                await bot.send_message(
                    target_id,
                    f"🎉 Добро пожаловать в альянс Dice!\n"
                    f"✅ Администратор зарегистрировал вас с ником: {player_name}\n\n"
                    f"Теперь вам доступен полный функционал бота!\n"
                    f"Используйте команду /start для просмотра доступных функций."
                )
            except:
                pass
        else:
            await message.reply("❌ Ошибка при регистрации пользователя")
            
@router.message(F.text.startswith("NICKS"))
async def handle_get_all_nick(message: types.Message, state: FSMContext):

    # Проверяем наличие чата в allowed_chats
    if not db.is_chat_allowed(message.chat.id):
        await message.answer("Этот чат не авторизован для использования данной команды.")
        return
    
    # Получаем всех пользователей, сортируем по player_name
    users_response = db.client.table('users')\
        .select('tag, player_name')\
        .order('player_name')\
        .execute()
    
    if not users_response.data:
        await message.answer("Список игроков пуст.")
        return
    
    # Формируем красивый список
    users_list = []
    for index, user in enumerate(users_response.data, 1):
        tag = user.get('tag', 'N/A')
        player_name = user.get('player_name', 'Без имени')
        users_list.append(f"{index}. {tag} - {player_name}")
    
    response_text = "📋 Список игроков:\n\n" + "\n".join(users_list)
    
    await message.answer(response_text)




















from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton

# Хендлер для добавления паттерна через JSON
@router.callback_query(F.data == "add_pattern")
async def cmd_add_pattern(callback: CallbackQuery, state: FSMContext):
    """Добавление нового паттерна"""
    await callback.message.answer('Введите новый паттерн в формате\n{"name": "DiceTeam", "elements": ["🎲","⚡","🎯"], "mas_elements": [["🎲"],["⚡"],["🎯"]]}')
    await state.set_state(RegistrationStates.waiting_pattern_add)
    await callback.answer()



@router.message(RegistrationStates.waiting_pattern_add)
async def process_pattern_selection(message: types.Message, state: FSMContext):
    """Добавление паттерна через JSON в сообщении"""
    try:
        data = json.loads(message.text)
        pattern_manager = PatternManager(db)
        await pattern_manager.create_pattern(
            data['name'],
            data['elements'],
            data['mas_elements']
        )
        
        await message.answer(f"✅Паттерн '{data['name']}' успешно создан!")

        
    except json.JSONDecodeError:
        await message.answer("❌Ошибка: Неверный формат JSON")
    except KeyError as e:
        await message.answer(f"❌Ошибка: Отсутствует поле {e}")
    await state.clear()
    

# Хендлер для выбора активного паттерна
@router.callback_query(F.data == "set_pattern")
async def cmd_set_pattern(callback: CallbackQuery, state: FSMContext):
    """Установка активного паттерна"""
    pattern_manager = PatternManager(db)
    patterns = await pattern_manager.get_all_patterns()
    
    if not patterns:
        await callback.message.answer("❌Нет доступных паттернов.")
        return
    
    # Создаем клавиатуру для выбора
    inline_buttons = []

    for pattern in patterns:
        status = "✅" if pattern.status == "Active" else "❌"
        inline_buttons.append([InlineKeyboardButton(text = f"{status} {pattern.pattern_name} (ID: {pattern.id})", callback_data=f"PATTERN {pattern.id}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    
    await callback.message.answer("Выберите паттерн для активации:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_pattern_selection)
    await callback.answer()


@router.callback_query(RegistrationStates.waiting_pattern_selection)
async def process_pattern_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора паттерна"""
    try:
        # Извлекаем ID из текста кнопки
        pattern_id = int(callback.data.split(" ")[-1])
        
        pattern_manager = PatternManager(db)
        await pattern_manager.set_active_pattern(pattern_id)
        
        await callback.message.answer("✅Паттерн успешно активирован!", reply_markup=types.ReplyKeyboardRemove())
        
        
    except (IndexError, ValueError):
        await callback.message.answer("❌Ошибка выбора паттерна. Попробуйте еще раз.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
