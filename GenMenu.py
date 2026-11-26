import json
import random


class GenMenu:
    def __init__(self):
        with open("eat_menu.json", "r", encoding='utf-8') as em_file:
            self.eat_menu = json.load(em_file)

        self.balance_cal = {"breakfast":20,"lunch":30,"dinner":30,"second_dinner":25,"snack":5} # Процент от суточного колаража

    def one_gram(self, num):
        # Принимает число в 100 грамм и переводит в 1
        return float(num) / 100

    def user_cpfc_to_CPFC(self,user_cpfc):
        # Переводит из 2500/120/60/400 в [2500,120,60,400]
        # ТУТПОТОМ НАПИШИ ПРОВЕРКУ НА ДУРАКА
        user_cpfc_list = user_cpfc.replace('/', ' ').split()

        return True, user_cpfc_list

    def gen_cpfc(self, weight, height, age, gender, activity, purpose):
        CPFC = [0,0,0,0]

        # BMR
        if gender == "men":
            BMR = 10 * weight + 6.25 * height - 5 * age + 5
        if gender == "women":
            BMR = 10 * weight + 6.25 * height - 5 * age - 161

        # KFA
        if activity == 1:
            KFA = 1.2
        elif activity == 2:
            KFA = 1.375
        elif activity == 3:
            KFA = 1.55
        elif activity == 4:
            KFA = 1.725
        elif activity == 5:
            KFA = 1.9

        # TDEE
        TDEE = BMR * KFA

        # Цель
        if purpose == "gain":
            CPFC[0] = TDEE + 200
        elif purpose == "loss":
            CPFC[0] = TDEE - 200
        elif purpose == "maintenance":
            CPFC[0] = TDEE

        CPFC[1] = (CPFC[0] * 0.30) / 4 # proteins
        CPFC[2] = (CPFC[0] * 0.25) / 9 # fats
        CPFC[3] = (CPFC[0] - (CPFC[1] * 4) - (CPFC[2] * 9)) / 4 # carbohydrates

        return CPFC

    def get_cpfc_to_item(self,item):
        # Принимает связку item+gram, перемножает начения и выводит кбжу элемента с учётом грамовки
        result = [
            float(self.one_gram(item[0]["calories"])) * item[1],
            float(self.one_gram(item[0]['proteins'])) * item[1],
            float(self.one_gram(item[0]['fats'])) * item[1],
            float(self.one_gram(item[0]['carbohydrates'])) * item[1]]
        return result

    def global_sum_cpfc_food(self, result_menu):
        # Cчитает общую каллорийность меню
        global_sum_cpfc_food = [0, 0, 0, 0]
        for food in result_menu:
            sum_cpfc_food = [0, 0, 0, 0]
            # print(food)
            for index, item in enumerate(result_menu[food]):
                # print(gram_list[food][index])
                cpfc_pls_gram = self.get_cpfc_to_item(result_menu[food][index])
                # print( item[0]['text'] + str(gram_list[food][index]) )
                sum_cpfc_food[0] += cpfc_pls_gram[0]
                sum_cpfc_food[1] += cpfc_pls_gram[1]
                sum_cpfc_food[2] += cpfc_pls_gram[2]
                sum_cpfc_food[3] += cpfc_pls_gram[3]

            global_sum_cpfc_food[0] += sum_cpfc_food[0]
            global_sum_cpfc_food[1] += sum_cpfc_food[1]
            global_sum_cpfc_food[2] += sum_cpfc_food[2]
            global_sum_cpfc_food[3] += sum_cpfc_food[3]

        return global_sum_cpfc_food

    def gen_ready_menu(self):
        # Запуск в терминале, генерирует случайные комбинации продуктов и принимает разрешение или отказ от сохранения
        max_len_item_menu = 4 # Максимальный список продуктов в пп
        random_bundle = []# Рандомная связка
        random_id_bundle = []
        copy_eat_menu = self.eat_menu['food'].copy() # Список продуктов
        with open("bundle_list.json", "r", encoding='utf-8') as em_file:
            bundle_f = json.load(em_file)

        # Генерация связки
        for _ in range(max_len_item_menu):
            random_bundle.append(random.choice(copy_eat_menu))

        #Создание айди связки
        random_id_bundle = [random_bundle[0]['id'],random_bundle[1]['id'],random_bundle[2]['id'],random_bundle[3]['id']]

        print(random_bundle)
        print(random_id_bundle)

        # Проверка на совпадение с существующими
        if random_id_bundle in self.eat_menu['ready_breakfast']:
            self.gen_ready_menu()
        elif random_id_bundle in self.eat_menu['ready_breakfast']:
            self.gen_ready_menu()
        elif random_id_bundle in self.eat_menu['ready_breakfast']:
            self.gen_ready_menu()

        for ead in random_bundle:
            print(" - " + str(ead['text']))

        # Обработка команд y/n/stop
        answer = input("B/ F/ S/ NO: ")

        if answer == "b":
            bundle_f['ready_breakfast'].append(random_id_bundle)
            with open("bundle_list.json", "w") as base_file:
                json.dump(bundle_f, base_file)
            self.gen_ready_menu()

        elif answer == "f":
            bundle_f['ready_food'].append(random_id_bundle)
            with open("bundle_list.json", "w") as base_file:
                json.dump(bundle_f, base_file)
            self.gen_ready_menu()
        elif answer == "s":
            bundle_f['ready_snack'].append(random_id_bundle)
            with open("bundle_list.json", "w") as base_file:
                json.dump(bundle_f, base_file)
            self.gen_ready_menu()
        elif answer == "n":
            self.gen_ready_menu()

    def get_item_menu(self,ead):
        # Достаёт рандомный элемент по готовому меню(с указанием типа)
        item_pos_ready_food = random.choice(self.eat_menu[ead])
        for id in item_pos_ready_food:
            for item_food in self.eat_menu['food']:
                if item_food['id'] == id:
                    if "allergens" in item_food:  # Если продукт содержит аллерген
                        if not self.allergens[item_food["allergens"]]:

                            print(item_pos_ready_food)
                            self.get_item_menu(ead)
        return item_pos_ready_food

    # ЭТАПЫ СОЗДАНИЯ МЕНЮ
    def fun_recepton_food_to_protocol(self, food_protocol):
        # Принимает айди блюд в приёме пищи и вставляет данные из таблицы

        # Получаем айди

        # Перебираем приёмы пищи
        for ead in list(food_protocol.keys()):
            print(ead)
            # рандомно добавляем список готовых блюд по приёму пищи
            if ead == "breakfast":
                item_pos_ready_food = self.get_item_menu("ready_breakfast")

            elif ead == "lunch" or ead == "dinner" or ead == "second_dinner":
                item_pos_ready_food = self.get_item_menu("ready_food")

            elif ead == "snack":
                item_pos_ready_food = self.get_item_menu("ready_snack")

            # заполняем food_protocol рандомными пп и добавляем граммы
            for id in item_pos_ready_food:
                for item_food in self.eat_menu['food']:
                    if item_food['id'] == id:
                        food_protocol[ead].append([item_food, 1])

            # Проверка на алергены

        return food_protocol

    def fun_recepton_gramm(self, menu):
        # Установка граммовки для каждого блюда

        # а = число каллорий / 2  -  основное блюдо
        # б = а / 2  -  побочные

        for food in menu.keys(): # Перебираем приёмы пищи
            for index_pos_protocol, item_pos_protocol in enumerate(menu[food]):  # перебираем позиции в приёме пищи
                target_gram_protocol = []
                c_target = 100 # Дальше будет делиться с каждой позицией в приёме пищи(%)
                len_food_list = len(menu[food])

                while len_food_list > 0: # Создаём протокол баланса еды в приёме пищи
                    if len_food_list > 1:
                        c_target = c_target / 2
                    len_food_list -= 1

                    target_gram_protocol.append(c_target)

                target_gram_cal =  (int(self.CPFC[0]) / 100 * self.balance_cal[food]) / 100 * target_gram_protocol[index_pos_protocol]  # % от каллорийности завтрака
                cal_food = self.get_cpfc_to_item([menu[food][index_pos_protocol][0], menu[food][index_pos_protocol][1]]) # Кбжу продукта с учётом грамовки

                # Прибавляем граммовку пока не выйдет за норму
                while target_gram_cal > int(cal_food[0]):

                    if "unit" in menu[food][index_pos_protocol][0]:  # Если продукт имеет стабильную единицу
                        menu[food][index_pos_protocol][1] += int(menu[food][index_pos_protocol][0]['unit'])
                    else: # Если продукт считается в граммах
                        menu[food][index_pos_protocol][1] += 1

                    cal_food = self.get_cpfc_to_item([menu[food][index_pos_protocol][0], menu[food][index_pos_protocol][1]])# Кбжу продукта с учётом грамовки

                # Защита от огромного веса продукта (max-size)
                if "max-size" in menu[food][index_pos_protocol][0]:# Если есть max-size
                    if menu[food][index_pos_protocol][1] > int(menu[food][index_pos_protocol][0]['max-size']):# Проверяем есть ли привышение max-size
                        menu[food][index_pos_protocol][1] = int(menu[food][index_pos_protocol][0]['max-size'])

    def gen_menu(self, CPFC_value, allergens_value):
        # Ответ будет текст

        # 2500/120/60/400

        self.CPFC = CPFC_value
        self.allergens = allergens_value
        self.perfect_percentage = [int(self.CPFC[0]),int(self.CPFC[1]),int(self.CPFC[2]),int(self.CPFC[3])]
        protocol = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "second_dinner": [],
            "snack": []
        }

        # Удаляем второй ужин если каллораж маленький
        if int(self.CPFC[0]) < 2300: # то удаляем пп
            del protocol['second_dinner']
            food_protocol = protocol.copy()
        else:
            food_protocol = protocol.copy()

        for i in range(len(self.perfect_percentage)): # Сбалансированная норма на приём пищи
            self.perfect_percentage[i] /= len(food_protocol)

        # Готовый список

        # ЗАПОЛНЕНИЕ МЕНЮ ПРОДУКТАМИ
        food_list = self.fun_recepton_food_to_protocol(food_protocol)

        #Проверка на совпадения обеда, ужина и 2-ужина
        if food_list['lunch'] == food_list['dinner']:
            food_list = self.fun_recepton_food_to_protocol(food_protocol)

        # НАСТРОЙКА ГРАМОВКИ
        self.fun_recepton_gramm(food_list)

        # Вывод в терминал развёрнутого меню
        # for ead in food_list:
        #     print(ead)
        #     for item_ead in food_list[ead]:
        #         print(" - "+str(item_ead))

        return food_list


if __name__ == "__main__":
    gm = GenMenu()

    #gm.gen_ready_menu()
    gm.gen_menu(gm.user_cpfc_to_CPFC('3600/120/60/400')[1], {"milk": True, "nuts": False, "honey": True})