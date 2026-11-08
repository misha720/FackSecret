import json
import random


class GenMenu:
    def __init__(self):
        with open("eat_menu.json", "r", encoding='utf-8') as em_file:
            self.eat_menu = json.load(em_file)

        self.balance_cal = {"breakfast":20,"lunch":40,"dinner":30,"snack":10} # Процент от суточного колаража

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



    # ЭТАПЫ СОЗДАНИЯ МЕНЮ
    def fun_recepton_food_to_protocol(self):
        # Принимает айди блюд в приёме пищи и вставляет данные из таблицы
        list_item_menu = []
        food_protocol = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snack": []
        }

        # Получаем айди

        # Перебираем приёмы пищи
        for ead in list(food_protocol.keys()):
            # настраиваем список готовых блюд по приёму пищи
            if ead == "breakfast":
                item_pos_ready_food = random.choice(self.eat_menu["ready_breakfast"])

            elif ead == "lunch" or ead == "dinner":
                item_pos_ready_food = random.choice(self.eat_menu["ready_food"])

            elif ead == "snack":
                item_pos_ready_food = random.choice(self.eat_menu["ready_snack"])

            for id in item_pos_ready_food:
                for item_food in self.eat_menu['food']:
                    if item_food['id'] == id:
                        food_protocol[ead].append([item_food, 1])

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

                #print(target_gram_protocol)

                target_gram_cal =  (int(self.CPFC[0]) / 100 * self.balance_cal[food]) / 100 * target_gram_protocol[index_pos_protocol]  # % от каллорийности завтрака
                #print((int(self.CPFC[0]) / 100 * self.balance_cal[food]))
                #print(target_gram_cal)
                cal_food = self.get_cpfc_to_item([menu[food][index_pos_protocol][0], menu[food][index_pos_protocol][1]])

                while target_gram_cal > int(cal_food[0]):
                    menu[food][index_pos_protocol][1] += 1
                    cal_food = self.get_cpfc_to_item([menu[food][index_pos_protocol][0], menu[food][index_pos_protocol][1]])

    def gen_menu(self, CPFC_value, allergens_value):
        # Ответ будет текст

        # 2500/120/60/400

        self.CPFC = CPFC_value
        self.allergens = allergens_value
        #print(allergens_value)
        self.perfect_percentage = [int(self.CPFC[0]) / 4,int(self.CPFC[1]) / 4,int(self.CPFC[2]) / 4,int(self.CPFC[3]) / 4] # Сбалансированная норма на приём пищи

        # Готовый список

        # ЗАПОЛНЕНИЕ МЕНЮ ПРОДУКТАМИ
        food_list = self.fun_recepton_food_to_protocol()

        #Проверка на совпадения обеда и ужина
        if food_list['lunch'] == food_list['dinner']:
            food_list = self.fun_recepton_food_to_protocol()

        # НАСТРОЙКА ГРАМОВКИ
        self.fun_recepton_gramm(food_list)

        return food_list


if __name__ == "__main__":
    gm = GenMenu()

    gm.gen_menu(gm.user_cpfc_to_CPFC('2500/120/60/400')[1], 0)