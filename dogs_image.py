import json
import requests
from tqdm import tqdm
import configparser

# Конфигурационные файлы
config = configparser.ConfigParser()
config.read('settings.ini')
token = config['Tokens']['yd_token']


class YD:
    def __init__(self, token):
        self.token = token
        self.url_yadisk = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_folder(self, breed):
        # Создаем папку на Я.Диске
        params = {'path': f'{breed}'}
        headers = {'Authorization': self.token}
        response = requests.put(self.url_yadisk,
                                params=params, headers=headers)
        if response.status_code == 201:
            print(f'Папка "{breed}" создана.')
        elif response.status_code == 409:
            print(f'Папка "{breed}" уже существует.')
        else:
            print(f'Ошибка при создании папки: '
                  f'{response.status_code}, {response.text}')

    def upload_file(self, filename, breed, img_url):
        # Сохраняем картинку
        path = f'{breed}/{filename}'
        params = {
            'path': path,
            'url': img_url
        }
        headers = {'Authorization': self.token}
        response = requests.post(
            self.url_yadisk + "/upload",
            params=params,
            headers=headers
            )
        if response.status_code == 202:
            print(f'Файл "{filename}" загружен.')
        else:
            print(f'Ошибка при загрузке файла: '
                  f'{response.status_code}, {response.text}')


def get_image(breed):
    # Получение списка пород
    response = requests.get('https://dog.ceo/api/breeds/list/all')
    if response.status_code != 200:
        raise ValueError(f'Ошибка при получении списка пород: '
                         f'{response.status_code}, {response.text}')
    all_dogs_breeds = response.json()['message']

    result = []
    if breed not in all_dogs_breeds:
        raise ValueError(f'Порода "{breed}" не найдена.')
    # Проверяем наличие под-пород, сохраняем ссылку и наименование картинки
    elif len(all_dogs_breeds[breed]) > 0:
        sub_breeds = all_dogs_breeds.get(breed)
        for sub_breed in sub_breeds:
            sub_breed_response = requests.get(
                f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random')
            if sub_breed_response.status_code != 200:
                raise ValueError(f'Ошибка при получении изображения: '
                                 f'{sub_breed_response.status_code}, '
                                 f'{sub_breed_response.text}')

            else:
                img_url = sub_breed_response.json()['message']
                filename = f'{breed}_{img_url.split('/')[-1]}'
                result.append({
                    'breed': breed,
                    'sub-breed': sub_breed,
                    'file': filename,
                    'url': img_url
                })

    else:
        response = requests.get(
            f'https://dog.ceo/api/breed/{breed}/images/random')
        if response.status_code != 200:
            raise ValueError(f'Ошибка при получении изображения: '
                             f'{response.status_code}, {response.text}')

        else:
            img_url = response.json()['message']
            filename = f'{breed}_{img_url.split('/')[-1]}'
            result.append({
                    'breed': breed,
                    'sub-breed': None,
                    'file': filename,
                    'url': img_url
                })
    return result


def save_json(result, breed):
    # Запись в JSON файл
    json_result = [{'file_name': item['file']} for item in result]
    with open(f"{breed}_images.json", "w") as f:
        json.dump(json_result, f, indent=4)

    return result


if __name__ == "__main__":
    breed = input("Введите название породы собаки: ")

    try:
        images_data = get_image(breed)
    except ValueError as err:
        print(err)
        exit(1)

    # Создаем экземпляр YD
    yd_instance = YD(token)

    # Создаем папку на Я.Диске
    yd_instance.create_folder(breed)

    # Загружаем картинку на Я.Диск с прогресс-баром
    for item in tqdm(images_data):
        yd_instance.upload_file(item['file'], breed, item['url'])

    # Формируем JSON-файл
    save_json(images_data, breed)
