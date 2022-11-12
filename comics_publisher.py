import os
import requests
import pathlib
import random
from urllib.parse import urlparse
from dotenv import load_dotenv


def download_img(image_details_url, path):
    response = requests.get(image_details_url)
    response.raise_for_status()
    decoded_response = response.json()
    url_for_download = decoded_response['img']
    path.parent.mkdir(exist_ok=True)
    photo_caption = decoded_response['alt']
    response = requests.get(url_for_download)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    return photo_caption


def get_upload_url(url, group_id, vk_token, api_version):
    url = f'{url}photos.getWallUploadServer'
    params = {'group_id': group_id, 'access_token': vk_token, 'v': api_version}
    response = requests.get(url, params)
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_img(upload_url, path_to_img,
               api_url, group_id,
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
        response = requests.post(f'{api_url}photos.saveWallPhoto', params)
        saved_photo_details = response.json()
        return saved_photo_details


def get_last_comic_num():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    num = response.json()['num']
    return num


def public_img(saved_photo_details, photo_caption,
               api_url, group_id, vk_token, api_version):
    url = f'{api_url}wall.post'
    img_owner_id = int(saved_photo_details['response'][0]['owner_id'])
    photo_id = saved_photo_details['response'][0]['id']
    params = {'attachments': f'photo{img_owner_id}_{photo_id}',
              'message': photo_caption,
              'owner_id': f'-{group_id}',
              'from_group': 1,
              'access_token': vk_token,
              'v': api_version}
    response = requests.post(url, params)
    response.raise_for_status()


def main():
    load_dotenv()
    comic_number = random.randint(1, get_last_comic_num())
    image_details_url = f'https://xkcd.com/{comic_number}/info.0.json'
    path = pathlib.Path.cwd() / f'comic.png'
    api_url = 'https://api.vk.com/method/'
    group_id = os.getenv('VK_GROUP_ID')
    vk_token = os.getenv('VK_TOKEN')
    api_version = os.getenv('API_VERSION')
    photo_caption = download_img(image_details_url, path)
    upload_url = get_upload_url(api_url, group_id, vk_token, api_version)
    saved_photo_details = upload_img(upload_url, path,
                                     api_url, group_id,
                                     vk_token, api_version)
    public_img(saved_photo_details,
               photo_caption,
               api_url, group_id,
               vk_token, api_version)
    path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
