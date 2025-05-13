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
        requests.put(self.url_yadisk, params=params, headers=headers)

    def upload_file(self, filename, breed, img_url):
        # Сохраняем картинку
        path = f'{breed}/{breed}_{filename}'
        params = {
            'path': path,
            'url': img_url
        }
        headers = {'Authorization': self.token}
        requests.post(self.url_yadisk + "/upload",
                      params=params, headers=headers)


def get_image(breed):
    # Получение списка пород
    response = requests.get('https://dog.ceo/api/breeds/list/all')
    all_dogs_breeds = response.json()['message']

    result = []
    # Проверяем наличие под-пород, сохраняем ссылку и наименование картинки
    if len(all_dogs_breeds[breed]) > 0:
        sub_breeds = all_dogs_breeds.get(breed)
        for sub_breed in sub_breeds:
            sub_breed_response = requests.get(
                f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random')
            img_url = sub_breed_response.json()['message']
            filename = img_url.split('/')[-1]
            result.append({
                'breed': breed,
                'sub-breed': sub_breed,
                'file': filename,
                'url': img_url
            })

    else:
        response = requests.get(
            f'https://dog.ceo/api/breed/{breed}/images/random')
        img_url = response.json()['message']
        filename = img_url.split('/')[-1]
        result.append({
                'breed': breed,
                'sub-breed': None,
                'file': filename,
                'url': img_url
            })
    # Вызов методов Я.Диска
    yd_instance = YD(token)
    yd_instance.create_folder(breed)
    # Прогресс-бар загрузки файлов
    for item in tqdm(result):
        yd_instance.upload_file(item['file'], breed, item['url'])
    json_result = [{'file_name': item['file']} for item in result]

    # Запись информации о загруженных файлах в JSON файл
    with open(f"{breed}_images.json", "w") as f:
        json.dump(json_result, f, indent=4)

    return result


if __name__ == "__main__":
    breed = input("Введите название породы собаки: ")
    images_data = get_image(breed)
