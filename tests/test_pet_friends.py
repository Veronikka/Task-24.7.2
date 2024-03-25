import pytest

from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_api_key_for_invalid_user(email="sadkfjlksdafjlksFDJLK", password="aksdjfhkasdhlfkj"):
    """ Проверяем что запрос api ключа возвращает статус 403, т.к. нету пользователя под таким логином и паролем"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_unsuccessful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о несуществующем питомце"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.update_pet_info(auth_key, "SKLDJFLKSDJFKLSD", name, animal_type, age)

    # Проверяем что статус ответа = 400, т.к. нельзя обновить информацию о несуществующем питомце
    assert status == 400


def test_successful_create_simple_pet(name="кот1", animal_type="кощка", age=4):
    """Проверяем что можно добавить питомца без фото с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_create_simple_pet_with_long_name(name="кот1"*2000, animal_type="кощка", age=8):
    """Проверяем что можно добавить питомца без фото с длинным именем"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_add_photo_to_simple_pet(pet_photo='images/cat2.jpg'):
    """Проверяем возможность добавления фото к питомцу"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить фото последнего питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.add_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        # Проверяем что статус ответа = 200
        assert status == 200
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_unsuccessful_add_photo_to_simple_pet(pet_photo='images/cat2.jpg'):
    """Проверяем возможность добавления фото к несуществующему питомцу"""

    # Получаем ключ auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_photo(auth_key, "KJDSFHHSKJDFHKSDJf", pet_photo)
    # Проверяем что статус ответа = 500, ошибка со стороны сервера
    assert status == 500


def test_successful_create_simple_pet_with_incorrect_age(name="котейка", animal_type="кощка!11"*100, age=7):
    """Проверяем что можно добавить питомца без фото с некорректным типом животного"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Ожидаем, что получим ошибку 4XX, т.к. тип животного некорректный
    assert status // 100 == 4


def test_unsuccessful_create_simple_pet_with_incorrect_age(name="котейка", animal_type="кощка!11", age=999_999_999):
    """Проверяем что можно добавить питомца без фото с некорректным возрастом"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Ожидаем, что получим ошибку 4XX, т.к. возраст животного некорректный
    assert status // 100 == 4


def test_add_new_pet_with_int_name(name=1111, animal_type='двортерьер',
                                     age=4, pet_photo='images/cat3.jpg'):
    """Проверяем что нельзя добавить питомца с цифрами вместо имени"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Ожидаем Attribute Error, т.к. имя не может быть числом
    with pytest.raises(AttributeError):
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)


def test_add_new_pet_with_int_animal_type(name="Котейка", animal_type=928347,
                                     age=4, pet_photo='images/cat3.jpg'):
    """Проверяем что нельзя добавить питомца с цифрами вместо породы"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Ожидаем Attribute Error, т.к. порода не может быть числом
    with pytest.raises(AttributeError):
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)


def test_successful_create_simple_pet_with_incorrect_age(name="котейка", animal_type="кощкаааа", age="какая-то строка"):
    """Проверяем что нельзя добавить питомца со строкой в графе возраста"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Ожидаем, что получим ошибку 4XX, т.к. возраст животного некорректный
    assert status // 100 == 4
