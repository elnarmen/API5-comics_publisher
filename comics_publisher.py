import os
import requests
import pathlib
import random
from urllib.parse import urlparse
from dotenv import load_dotenv


def download_img(comic_number):
    response = requests.get(f'https://xkcd.com/{comic_number}/info.0.json')
    response.raise_for_status()
    url_for_download = response.json()['img']
    response = requests.get(url_for_download)
    response.raise_for_status()
    with open('comic.png', 'wb') as file:
        file.write(response.content)


def get_photo_caption(comic_number):
    response = requests.get(f'https://xkcd.com/{comic_number}/info.0.json')
    response.raise_for_status()
    photo_caption = response.json()['alt']
    return photo_caption


def get_upload_url(group_id, vk_token, api_version):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {'group_id': group_id, 'access_token': vk_token, 'v': api_version}
    response = requests.get(url, params)
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    upload_url = decoded_response['response']['upload_url']
    return upload_url


def upload_img(upload_url, path_to_img, group_id,
               vk_token, api_version):
    with open(path_to_img, 'rb') as file:
        files = {'file1': file}
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    decoded_response = response.json()
    params = {
        'server': decoded_response['server'],
        'photo': decoded_response['photo'],
        'hash': decoded_response['hash'],
        'access_token': vk_token,
        'group_id': group_id,
        'v': api_version,
    }
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params)
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    img_owner_id = decoded_response['response'][0]['owner_id']
    photo_id = decoded_response['response'][0]['id']
    return img_owner_id, photo_id


def get_last_comic_num():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    num = response.json()['num']
    return num


def post_image(img_owner_id, photo_id, photo_caption, group_id, vk_token, api_version):
    url = 'https://api.vk.com/method/wall.post'
    params = {'attachments': f'photo{img_owner_id}_{photo_id}',
              'message': photo_caption,
              'owner_id': f'-{group_id}',
              'from_group': 1,
              'access_token': vk_token,
              'v': api_version}
    response = requests.post(url, params)
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])

def main():
    load_dotenv()
    comic_number = random.randint(1, get_last_comic_num())
    path = pathlib.Path.cwd() / f'comic.png'
    group_id = os.getenv('VK_GROUP_ID')
    vk_token = os.getenv('VK_TOKEN')
    api_version = os.getenv('API_VERSION')
    try:
        download_img(comic_number)
        photo_caption = get_photo_caption(comic_number)
        upload_url = get_upload_url(group_id, vk_token, api_version)
        img_owner_id, photo_id = upload_img(upload_url, path, group_id,
                                            vk_token, api_version)
        post_image(img_owner_id, photo_id, photo_caption,
                   group_id, vk_token, api_version)
    finally:
        path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
