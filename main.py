#   IMPORTS
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import json
import os
from loguru import logger
logger.add("debug.log", rotation="00:00", retention="1 week")
import difflib
from GenMenu import GenMenu

# AIOGRAM
#BOT_TOKEN = "8676203705:AAGwQA8bIM8NlKidODj6VpmWPVuqM1lXNqo" # prod
BOT_TOKEN = "8682867061:AAHFLN1LaKnPFDl0iQMcKv22VcY9q4BezV0" # test
ADMIN = [1020432840]  # Список админов
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


#   VALUE
if os.path.isfile("database.json"):
    with open("database.json", "r") as db_file:
        database = json.load(db_file)
gen_menu = GenMenu()


#   FUN
def create_user(u_id):# Coздаёт базу пользователя
    new_user = {"id": u_id,
                "gender": "",
                "age": 0,
                "purpose": "maintenance",  # maintenance\loss\gain
                "height": 0,
                "weight": 0,
                "activity": 0,
                "allergens": {"milk": False, "nuts": False, "honey": False},
                "CPFC": [0, 0, 0, 0]}

    database['users'].append(new_user)
    logger.success("Зарегистрирован новый пользователь - " + str(u_id))
    # Сохранение в файл
    with open("database.json", "w") as base_file:
        json.dump(database, base_file)


# FSM
class Reg(StatesGroup):
    gender = State() # пол человека
    age = State()
    purpose = State() # цель, поддержание/набор/похудение
    height = State() # рост человека
    weight = State() # вес человека
    activity = State()  # активность человека
    allergy_honey = State() # Алергия мёд
    allergy_nuts = State()  # Алергия мёд
    allergy_milk = State()  # Алергия мёд
    choosing_cpfc = State()


# OnStart
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    logger.info("OnClickStart - " + str(message.from_user.id))

    # Если пользователь зашёл первый раз, создать его анкету
    users_list_id = []
    for user_item in database['users']:
        users_list_id.append(user_item['id'])

    if message.from_user.id not in users_list_id:

        create_user(message.from_user.id) # Coздаёт базу пользователя

        # Настройка Инлайна
        inline_btn_start = InlineKeyboardButton(text='Регистрация', callback_data="btn_create_user")
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[inline_btn_start]])

        # Отправка лого
        await bot.send_photo(message.chat.id, photo=types.FSInputFile("logo.jpg"))

        # Отправка сообщения
        await bot.send_message(
            message.from_user.id,
            text='<b>Добро пожаловать в FackSecret</b>😈\n\nЯ создан помочь с тем, что бы ты больше не думал <em>"Что сегодня съесть?"</em>. Пока у меня не большой функционал, но я стараюсь, а тебе приятного пользования.\n\nДавай я тебе помогу подобрать меню на сегодня?',
            reply_markup=inline_kb)

    else: # Пользователь существует
        inline_btn_start = InlineKeyboardButton(text='Начать', callback_data="btn_global_menu")
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[inline_btn_start]])

        await bot.send_photo(message.chat.id, photo=types.FSInputFile("logo.jpg"))

        await bot.send_message(
            message.from_user.id,
            text='<b>Добро пожаловать в FackSecret</b>😈\n\nЯ создан помочь с тем, что бы ты больше не думал <em>"Что сегодня съесть?"</em>. Пока у меня не большой функционал, но я стараюсь, а тебе приятного пользования.\n\nДавай я тебе помогу подобрать меню на сегодня?',
            reply_markup=inline_kb)



#   РЕГИСТРАЦИЯ
@dp.callback_query(F.data == 'btn_create_user')
async def reg_gender(call: CallbackQuery, state: FSMContext):
    logger.info("Пользователь:" + str(call.from_user.id) + " начал регистрацию")

    await state.set_state(Reg.gender)
    await bot.send_message(call.from_user.id, text="Напиши свой гендер")

@dp.message(Reg.gender)
async def reg_purpose(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил для себя гендер - " + str(message.text))

    control_list = ["мужчина", "девушка", "женщина"]
    var_gender = ""

    try:
        word = difflib.get_close_matches(message.text.lower(), control_list, n=1)[0]

        # Фильтр
        if word == "мужчина":
            var_gender = "men"
        elif word == "девушка":
            var_gender = "women"
        elif word == "женщина":
            var_gender = "women"

        # Запись
        await state.update_data(gender=var_gender)
        await state.set_state(Reg.purpose)
        await bot.send_message(message.from_user.id,
            text="Какая у тебя цель? Набор массы, похудение или поддержание?")

    except IndexError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, введи пожалуйста что то из этого - "мужчина","женщина"')
        await state.set_state(Reg.gender)
        logger.error(IndexError)

@dp.message(Reg.purpose)
async def reg_height(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил цель - " + str(message.text))

    control_list = ["набор", "похудение", "поддержание"]
    var_purpose = ""

    try:
        word = difflib.get_close_matches(message.text.lower(), control_list, n=1)[0]

        # Фильтр
        if word == "набор":
            var_purpose = "gain"
        elif word == "похудение":
            var_purpose = "loss"
        elif word == "поддержание":
            var_purpose = "maintenance"

        await state.update_data(purpose=var_purpose)
        await state.set_state(Reg.height)
        await bot.send_message(message.from_user.id, text="Какой у тебя рост?")

    except IndexError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, введи пожалуйста что то из этого - "набор","похудение","поддержание"')
        await state.set_state(Reg.purpose)
        logger.error(IndexError)

@dp.message(Reg.height)
async def reg_weight(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил рост - " + str(message.text))
    var_height = ""

    # Фильтр
    try: # Проверка на число
        var_height = int(message.text)

        if var_height < 300 and var_height > 20:# Проверка на величину
            await state.update_data(height=var_height)
            await state.set_state(Reg.weight)
            await bot.send_message(message.from_user.id, text="Какой у тебя вес?")
        else:
            await bot.send_message(message.from_user.id, text='Что-то ты огромный, давай по честному')
            await state.set_state(Reg.height)
            logger.error("Рост слишком большой")

    except ValueError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, мне нужна сама цифра')
        await state.set_state(Reg.height)
        logger.error(ValueError)

@dp.message(Reg.weight)
async def reg_activity(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил вес - " + str(message.text))
    var_weight = ""

    # Фильтр
    try:# Проверка на число
        var_weight = int(message.text)

        if var_weight < 300 and var_weight > 20:# Проверка на величину
            await state.update_data(weight=var_weight)
            await state.set_state(Reg.activity)
            await bot.send_message(message.from_user.id,
                text="Какая у тебя активность?\n\nВыбери цифру, под которой узнаешь себя:\n1 - Я большую часть времени сижу, мало двигаюсь\n2 - Слегка активен. Частенько выхожу на улицу, но не на долго\n3 - Я тренируюсь 3-4 раза в неделю\n4 - Я тяжело тренируюсь каждый день\n5 - У меня тяжёлая физическая работа или спорт дважды в день")
        else:
            await bot.send_message(message.from_user.id, text='Не можешь ты столько весить, давай ещё раз')
            await state.set_state(Reg.weight)
            logger.error("Вес слишком большой")

    except ValueError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, мне нужна сама цифра на весах')
        await state.set_state(Reg.weight)
        logger.error(ValueError)

@dp.message(Reg.activity)
async def reg_allergy_honey(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил активность - " + str(message.text))
    var_activity = ""

    # Фильтр
    try:
        var_activity = int(message.text)

        if var_activity in [1,2,3,4,5]:# Проверка на требуемый диапозон
            await state.update_data(activity=var_activity)
            await state.set_state(Reg.age)
            await bot.send_message(message.from_user.id, text="Сколько тебе лет?")
        else:
            await bot.send_message(message.from_user.id, text='Какая то ошибка, выбери число от 1 до 5')
            await state.set_state(Reg.activity)
            logger.error("Не правильно указали активность")

    except ValueError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, выбери число от 1 до 5')
        await state.set_state(Reg.activity)
        logger.error(ValueError)

@dp.message(Reg.age)
async def reg_allergy_honey(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил возраст - " + str(message.text))
    var_age = ""

    # Фильтр
    try:
        var_age = int(message.text)

        if var_age < 100:# Проверка на требуемый диапозон
            await state.update_data(age=var_age)
            await state.set_state(Reg.allergy_honey)
            await bot.send_message(message.from_user.id, text="У тебя есть алергия на мёд?")
        else:
            await bot.send_message(message.from_user.id, text='Тебе не может быть столько')
            await state.set_state(Reg.age)
            logger.error("Не правильно указали возраст")

    except ValueError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, укажите возраст цифрой')
        await state.set_state(Reg.age)
        logger.error(ValueError)

@dp.message(Reg.allergy_honey)
async def reg_allergy_nuts(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил аллергию на мёд - " + str(message.text))
    control_list = ["да", "нет"]
    var_allergy_honey = ""

    try:
        word = difflib.get_close_matches(message.text.lower(), control_list, n=1)[0]

        # Фильтр
        if word == "нет":
            var_allergy_honey = False
        elif word == "да":
            var_allergy_honey = True

        await state.update_data(allergy_honey=var_allergy_honey)
        await state.set_state(Reg.allergy_nuts)
        await bot.send_message(message.from_user.id, text="У тебя есть аллергия на орехи?")

    except IndexError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, выбери "да" или "нет"')
        await state.set_state(Reg.allergy_honey)
        logger.error(IndexError)

@dp.message(Reg.allergy_nuts)
async def reg_allergy_milk(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил аллергию на орехи - " + str(message.text))
    control_list = ["да", "нет"]
    var_allergy_nuts = ""

    try:
        word = difflib.get_close_matches(message.text.lower(), control_list, n=1)[0]

        # Фильтр
        if word == "нет":
            var_allergy_nuts = False
        elif word == "да":
            var_allergy_nuts = True

        await state.update_data(allergy_nuts=var_allergy_nuts)
        await state.set_state(Reg.allergy_milk)
        await bot.send_message(message.from_user.id, text="У тебя есть аллергия на молоко?")

    except IndexError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, выбери "да" или "нет"')
        await state.set_state(Reg.allergy_nuts)
        logger.error(IndexError)

@dp.message(Reg.allergy_milk)
async def reg_finish(message: types.Message, state: FSMContext):
    logger.info("Пользователь:" + str(message.from_user.id) + " установил аллергию на молоко - " + str(message.text))
    control_list = ["да", "нет"]
    var_allergy_milk = ""

    try:
        word = difflib.get_close_matches(message.text.lower(), control_list, n=1)[0]

        # Фильтр
        if word == "нет":
            var_allergy_milk = False
        elif word == "да":
            var_allergy_milk = True

        await state.update_data(allergy_milk=var_allergy_milk)
        data = await state.get_data()
        logger.debug(data)

        # Расчёт кбжу
        CPFC = gen_menu.gen_cpfc(data['weight'], data['height'], data['age'], data['gender'], data['activity'], data['purpose'])

        # Загрузка данных в базу клиента
        for user_index, user_item in enumerate(database['users']):
            if user_item['id'] == message.from_user.id:
                # Обработка данных
                database['users'][user_index]['gender'] = data['gender']
                database['users'][user_index]['age'] = data['age']
                database['users'][user_index]['purpose'] = data['purpose']
                database['users'][user_index]['height'] = data['height']
                database['users'][user_index]['weight'] = data['weight']
                database['users'][user_index]['activity'] = data['activity']
                database['users'][user_index]['allergens'] = {"milk": data['allergy_milk'], "nuts": data['allergy_nuts'], "honey": data['allergy_honey']}
                database['users'][user_index]['CPFC'] = [int(CPFC[0]),int(CPFC[1]),int(CPFC[2]),int(CPFC[3])]

        # Сохранение
        with open("database.json", "w") as base_file:
            json.dump(database, base_file)

        # Настройка Инлайна
        inline_btn_start = InlineKeyboardButton(text='Начать', callback_data="btn_global_menu")
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[inline_btn_start]])

        # Отправка сообщения
        await bot.send_message(
            message.from_user.id,
            text='Отлично, я узнал всё что мне необходимо. Можем начинать!',
            reply_markup=inline_kb)
        
        await state.clear()

    except IndexError:
        await bot.send_message(message.from_user.id, text='Какая то ошибка, выбери "да" или "нет"')
        await state.set_state(Reg.allergy_milk)
        logger.error(IndexError)



# CLICK - "btn_global_menu"
@dp.callback_query(F.data == 'btn_global_menu')
async def inline_btn_get_menu(call: CallbackQuery, state: FSMContext):
    for user_index, user_item in enumerate(database['users']):
        if user_item['id'] == call.from_user.id:# Пользователь найден
            await state.clear()

            text_btn_CPFC = "Изменить КБЖУ : " + str(user_item['CPFC'][0]) + "/" + str(user_item['CPFC'][1]) + "/" + str(user_item['CPFC'][2]) + "/" + str(user_item['CPFC'][3])

            # Inline
            inline_btn_CPFC = InlineKeyboardButton(text=text_btn_CPFC, callback_data="btn_set_CPFC")
            inline_btn_get_menu = InlineKeyboardButton(text='Создать меню', callback_data="btn_get_menu")
            inline_btn_gen_cpfc = InlineKeyboardButton(text='Расчитать КБЖУ', callback_data="btn_gen_cpfc")
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_CPFC], [inline_btn_gen_cpfc], [inline_btn_get_menu]])

            await bot.send_message(
                call.from_user.id,
                text='<b>Главное меню</b>\n\nЯ автаматически расчитал для тебя калораж, но если хочешь, можешь его изменить. Так же тут много других кнопочек, но главная - Составить меню\n\nВажное НО. Любые расчёты — это лишь ориентир. В процессе следи за весом и самочувствием, при необходимости корректируй рацион.',
                reply_markup=inline_kb)

            break

    else: # Пользователь не найден
            create_user(call.from_user.id)  # Coздаёт базу пользователя

            # Настройка Инлайна
            inline_btn_start = InlineKeyboardButton(text='Регистрация', callback_data="btn_create_user")
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[[inline_btn_start]])

            # Отправка лого
            await bot.send_photo(call.from_user.id, photo=types.FSInputFile("logo.jpg"))

            # Отправка сообщения
            await bot.send_message(
                call.from_user.id,
                text='<b>Добро пожаловать в FackSecret</b>😈\n\nЯ создан помочь с тем, что бы ты больше не думал <em>"Что сегодня съесть?"</em>. Пока у меня не большой функционал, но я стараюсь, а тебе приятного пользования.\n\nДавай я тебе помогу подобрать меню на сегодня?',
                reply_markup=inline_kb)

#   НАСТРАИВАЕМЫЕ СТАТЫ
# КБЖУ
@dp.message(Reg.choosing_cpfc)
async def cpfc_chosen(message: types.Message, state: FSMContext):
    for user_index, user_item in enumerate(database['users']):
        if user_item['id'] == message.from_user.id:  # Пользователь найден
            logger.debug(gen_menu.user_cpfc_to_CPFC(message.text)[1])
            database['users'][user_index]['CPFC'] = gen_menu.user_cpfc_to_CPFC(message.text)[1]

            # Сохранение в файл
            with open("database.json", "w") as base_file:
                json.dump(database, base_file)

            await state.clear()

    inline_btn_global_menu = InlineKeyboardButton(text='Назад', callback_data="btn_global_menu")
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[[inline_btn_global_menu]])
    await bot.send_message(
        message.from_user.id,
        text='✅ Отлично, я записал твоё КБЖУ',
        reply_markup=inline_kb)
    logger.success("Пользователь:"+str(message.from_user.id)+" установил для себя КБЖУ - "+str(message.text))
@dp.callback_query(F.data == 'btn_set_CPFC')
async def inline_btn_CPFC(call: CallbackQuery, state: FSMContext):
    # Устанавливаем пользователю состояние "выбирает кбжу"
    await state.set_state(Reg.choosing_cpfc)
    await bot.send_message(
        call.from_user.id,
        text='Укажи своё КБЖУ в формате "каллории/белки/жиры/углеводы"\n\n<b>Например: 2500/120/60/400</b>')



# CLICK - "btn_gen_cpfc"
@dp.callback_query(F.data == 'btn_gen_cpfc')
async def inline_btn_gen_cpfc(call: CallbackQuery):
    for user_index, user_item in enumerate(database['users']):
        if user_item['id'] == call.from_user.id:# Пользователь найден
            await call.message.delete()
            CPFC = gen_menu.gen_cpfc(user_item['weight'], user_item['height'], user_item['age'],
                                     user_item['gender'], user_item['activity'],user_item['purpose'])

            database['users'][user_index]['CPFC'] = [int(CPFC[0]),int(CPFC[1]),int(CPFC[2]),int(CPFC[3])]

            # Сохранение
            with open("database.json", "w") as base_file:
                json.dump(database, base_file)

            inline_btn_global_menu = InlineKeyboardButton(text='Назад', callback_data="btn_global_menu")
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[[inline_btn_global_menu]])

            await bot.send_message(
                call.from_user.id,
                text='<b>КБЖУ обновлено</b>\n\nСмотри, я взял твой рост, вес и тд. и на их основе расчитал для тебя КБЖУ по формуле <em>Миффлина - Сан Жеора.</em>\nТеперь возвращайся назад в меню', reply_markup=inline_kb)

# CLICK - "btn_get_menu"
@dp.callback_query(F.data == 'btn_get_menu')
async def inline_btn_get_menu(call: CallbackQuery):
    for user_item in database['users']:
        if user_item['id'] == call.from_user.id:
            logger.info("Пользователь:"+str(call.from_user.id)+" заказал меню на день")
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
            inline_btn_global_menu = InlineKeyboardButton(text='Назад', callback_data="btn_global_menu")
            inline_kb = InlineKeyboardMarkup(
                inline_keyboard=[[inline_get_menu],[inline_btn_global_menu]])

            await bot.send_message(
                call.from_user.id,
                text='✅ Вот твоё меню на сегодня:\n\n'+text_menu, reply_markup=inline_kb)



async def main() -> None:
    # Запускаем получение обновлений
    try:
        logger.success("Скрипт запущен")
        await dp.start_polling(bot)
    except Exception:
        logger.error(Exception)


if __name__ == "__main__":
    asyncio.run(main())