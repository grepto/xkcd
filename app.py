import requests
import random
import os

VK_TOKEN = os.getenv('VK_TOKEN')
VK_GROUP_ID = os.getenv('VK_GROUP_ID')

VK_URL = 'https://api.vk.com/method'
payloads = {
    'access_token': VK_TOKEN,
    'v': 5.95
}


def get_wall_upload_server():
    method_url = f'{VK_URL}/photos.getWallUploadServer'
    payloads['group_id'] = VK_GROUP_ID
    response = requests.get(method_url, params=payloads)
    response.raise_for_status()
    if response.json().get('error', None):
        return None
    return response.json()['response']['upload_url']


def upload_photo(upload_url, photo):
    image_file_descriptor = open(photo, 'rb')
    files = {'photo': image_file_descriptor}
    response = requests.post(upload_url, files=files)
    image_file_descriptor.close()
    response.raise_for_status()
    if response.json()['photo'] == '[]':
        return None
    return response.json()


def save_wall_photo(uploaded_photo):
    method_url = f'{VK_URL}/photos.saveWallPhoto'
    payloads.update({
            'group_id': VK_GROUP_ID,
            'photo': uploaded_photo['photo'],
            'server': uploaded_photo['server'],
            'hash': uploaded_photo['hash'],
            })
    response = requests.get(method_url, params=payloads)
    response.raise_for_status()
    if response.json().get('error', None):
        return None
    return response.json()['response'][0]


def post_photo(saved_photo, message=None):
    method_url = f'{VK_URL}/wall.post'
    payloads.update({
            'owner_id': f'-{VK_GROUP_ID}',
            'from_group': 1,
            'message': message,
            'attachments': f'photo{saved_photo["owner_id"]}_{saved_photo["id"]}',
            })
    response = requests.get(method_url, params=payloads)
    response.raise_for_status()
    return response.json()


def post_to_wall(photo, message):
    upload_server = get_wall_upload_server()
    uploaded_photo = upload_photo(upload_server, photo)
    saved_photo = save_wall_photo(uploaded_photo)
    post_photo(saved_photo, message)


def download_file(file_url, file_name):
    response = requests.get(file_url)
    if not response.ok:
        return None
    with open(file_name, 'wb') as file:
        file.write(response.content)


def get_xkcd_comics(comics_id=''):
    url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def post_random_comics():
    last_comics_id = get_xkcd_comics()['num']
    comics_id = random.randint(1, last_comics_id)
    xkcd_comics = get_xkcd_comics(comics_id)
    file_url = xkcd_comics['img']
    file_name = file_url.rsplit('/', 1)[1]
    download_file(file_url, file_name)
    post_to_wall(file_name, xkcd_comics['transcript'])
    os.remove(file_name)


if __name__ == '__main__':
    post_random_comics()
