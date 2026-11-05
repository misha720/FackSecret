#   IMPORTS
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import json

from GenMenu import GenMenu

# AIOGRAM
BOT_TOKEN = "8676203705:AAFklawit4ELDBGxt6RCYOqJdCW4dyDoO-E"
ADMIN = [1020432840]  # Список админов
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

#   VALUE
with open("database.json", "r") as db_file:
    database = json.load(db_file)
gen_menu = GenMenu()

class Set_CPFC_FSM(StatesGroup):
    choosing_cpfc = State()

# OnStart
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    print("start")
    inline_btn_start = InlineKeyboardButton(text='Начать', callback_data="btn_start")
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[[inline_btn_start]])

    await bot.send_photo(message.chat.id, photo=types.FSInputFile("logo.jpg"))

    await bot.send_message(
        message.from_user.id,
        text='<b>Добро пожаловать в FackSecret</b>😈\n\nЯ создан помочь с тем, что бы ты больше не думал <em>"Что сегодня съесть?"</em>. Пока у меня не большой функционал, но я стараюсь, а тебе приятного пользования.\n\nДавай я тебе помогу подобрать меню на сегодня?',
        reply_markup=inline_kb)

# CLICK - "btn_start"
@dp.callback_query(F.data == 'btn_start')
async def inline_btn_get_menu(call: CallbackQuery, state: FSMContext):

    # Если пользователь зашёл первый раз, создать его анкету
    users_list_id = []
    for user_item in database['users']:
        users_list_id.append(user_item['id'])

    if call.from_user.id not in users_list_id:
        new_user = {"id": call.from_user.id,
                    "allergens": [0],
                    "CPFC": [0, 0, 0, 0]}

        database['users'].append(new_user)
        # Сохранение в файл
        with open("database.json", "w") as base_file:
            json.dump(database, base_file)

    for user_index, user_item in enumerate(database['users']):

        # Пользователь найден
        if user_item['id'] == call.from_user.id:

            # Проверка FSM
            fsm_status = await state.get_state()
            if fsm_status != None and fsm_status[13:] == 'choosing_cpfc':
                fsm_cpfc = str(dict(await state.get_data())['choosing_cpfc'])

                # Jтработка проверки на дурака
                if gen_menu.user_cpfc_to_CPFC(fsm_cpfc)[0]:
                    database['users'][user_index]['CPFC'] = gen_menu.user_cpfc_to_CPFC(fsm_cpfc)[1]

                    # Сохранение в файл
                    with open("database.json", "w") as base_file:
                        json.dump(database, base_file)

                    await state.clear()
                else:
                    # Error
                    print("error")

            if len(user_item['allergens']) != 0:
                text_btn_allergens = '✔️ Изменить состав аллергенов'
            else:
                text_btn_allergens = '❌ Указать алергенны'

            text_btn_CPFC = "Указать КБЖУ : " + str(user_item['CPFC'][0]) + "/" + str(user_item['CPFC'][1]) + "/" + str(user_item['CPFC'][2]) + "/" + str(user_item['CPFC'][3])

            # Inline
            inline_btn_allergens = InlineKeyboardButton(text=text_btn_allergens, callback_data="btn_set_allergens")
            inline_btn_CPFC = InlineKeyboardButton(text=text_btn_CPFC, callback_data="btn_set_CPFC")
            inline_btn_get_menu = InlineKeyboardButton(text='Создать меню', callback_data="btn_get_menu")
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_CPFC], [inline_btn_get_menu]]) # Без алергена
            #inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_allergens], [inline_btn_CPFC], [inline_btn_get_menu]]) # С алергеном

            await bot.send_message(
                call.from_user.id,
                text='Что бы подобрать меню для тебя, мне нужно знать некоторые моменты...\n\n<em>Настрой предпочтения и нажми <b>"Создать меню"</b></em>',
                reply_markup=inline_kb)

# CLICK - "btn_set_allergens"
# @dp.callback_query(F.data == 'btn_set_allergens')
# async def inline_btn_allergens(call: CallbackQuery):
#     print('alerg')
#     for user_index, user_item in enumerate(database['users']):
#         if user_item['id'] == call.from_user.id:
#
#             # Если он тут первый раз
#             if user_item['allergens'] == []:
#                 return
#     # Inline
#     #allergen_zero = InlineKeyboardButton(text="Алергии нет", callback_data="btn_set_allergens")
#     #allergen_zero = InlineKeyboardButton(text="Молоко", callback_data="btn_set_allergens")
#     #allergen_zero = InlineKeyboardButton(text="Орехи", callback_data="btn_set_allergens")
#     allergen_zero = InlineKeyboardButton(text="Цитрусовые", callback_data="btn_set_allergens")
#     inline_kb = InlineKeyboardMarkup(
#         inline_keyboard=[[allergen_zero]])
#
#     await bot.send_message(
#         call.from_user.id,
#         text='Учитывать аллергены это очень важно при составлении плана питания, по этому ты можешь их указать, а я подберу безопасное меню индивидуально под тебя',
#         reply_markup=inline_kb)

# CLICK - "btn_set_CPFC"
@dp.message(Set_CPFC_FSM.choosing_cpfc)
async def cpfc_chosen(message: types.Message, state: FSMContext):
    await state.update_data(choosing_cpfc=message.text)

    inline_btn_start = InlineKeyboardButton(text='Назад', callback_data="btn_start")
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[[inline_btn_start]])
    await bot.send_message(
        message.from_user.id,
        text='✅ Отлично, я записал твоё КБЖУ',
        reply_markup=inline_kb)
@dp.callback_query(F.data == 'btn_set_CPFC')
async def inline_btn_CPFC(call: CallbackQuery, state: FSMContext):
    await bot.send_message(
        call.from_user.id,
        text='Укажи своё КБЖУ в формате "каллории/белки/жиры/углеводы"\n\n<b>Например: 2500/120/60/400</b>')

    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(Set_CPFC_FSM.choosing_cpfc)



# CLICK - "btn_get_menu"
@dp.callback_query(F.data == 'btn_get_menu')
async def inline_btn_get_menu(call: CallbackQuery):
    for user_item in database['users']:
        if user_item['id'] == call.from_user.id:

            # Удаление сообщения при замене меню
            if call.message.text[0] == "✅":# детектим замену
                await call.message.delete()

            result_menu = gen_menu.gen_menu(user_item['CPFC'], user_item['allergens'])
            text_menu = ""
            type_food = "" # завтрак обед ужин перекус

            for food_intake in result_menu: # перебираем приёмы пищи

                if food_intake == "breakfast":
                    type_food = "<b>Завтрак:</b>\n"
                elif food_intake == "lunch":
                    type_food = "<b>Обед:</b>\n"
                elif food_intake == "dinner":
                    type_food = "<b>Ужин:</b>\n"
                elif food_intake == "snack":
                    type_food = "<b>Перекус:</b>\n"
                text_menu += type_food

                for item_food_intake in result_menu[food_intake]: # Перебираем каждое блюдо
                    text_menu += "<em>" + item_food_intake[0]['text'] + "</em> - " + str(item_food_intake[1]) + "г.\n"
                text_menu += "\n"

            global_sum_cpfc_food = gen_menu.global_sum_cpfc_food(result_menu)
            text_menu += "<b>Общая каллорийность - </b>" + str(int(global_sum_cpfc_food[0])) + " / " + str(int(global_sum_cpfc_food[1])) + " / " + str(int(global_sum_cpfc_food[2])) + " / " + str(int(global_sum_cpfc_food[3]))

            inline_get_menu = InlineKeyboardButton(text='🔄 Заменить', callback_data="btn_get_menu")
            inline_start = InlineKeyboardButton(text='Назад', callback_data="btn_start")
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[[inline_get_menu],[inline_start]])

            await bot.send_message(
                call.from_user.id,
                text='✅ Вот твоё меню на сегодня:\n\n'+text_menu, reply_markup=inline_kb)



async def main() -> None:
    # Запускаем получение обновлений
    try:
        await dp.start_polling(bot)
        print("run")
    except Exception:
        print(Exception)


if __name__ == "__main__":
    asyncio.run(main())