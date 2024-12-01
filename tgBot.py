import requests
from io import BytesIO
import json

from image_processing import replace_colors
from halftone_effect_with_crosses import halftone_effect

token_path = 'token.txt'


def get_token(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()
        return token
    except Exception as e:
        print(f"Произошла ошибка при чтении токена: {e}")
        return None


TOKEN = get_token(token_path)
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

colors = {
    'colors1': [(196, 243, 56), (27, 27, 27)],
    'colors2': [(33, 82, 203), (27, 27, 27)],
    'colors3': [(252, 68, 15), (27, 27, 27)]
}


def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    response = requests.get(url, params=params)
    return response.json()


def send_message_with_buttons(chat_id, text, buttons):
    url = f"{BASE_URL}/sendMessage"
    reply_markup = {
        "inline_keyboard": buttons
    }
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(reply_markup)
    }
    requests.post(url, data=data)


def download_file(file_id):
    url = f"{BASE_URL}/getFile"
    response = requests.get(url, params={"file_id": file_id})
    file_path = response.json()["result"]["file_path"]

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    file_response = requests.get(file_url)
    return BytesIO(file_response.content)


def send_photo(chat_id, photo):
    url = f"{BASE_URL}/sendPhoto"
    files = {"photo": photo}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)


def main():
    last_update_id = None
    image_cache = {}

    while True:
        updates = get_updates(last_update_id)
        if updates.get("result"):
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                message = update.get("message")
                callback_query = update.get("callback_query")

                if message:
                    chat_id = message["chat"]["id"]
                    print(chat_id)
                    if "photo" in message:
                        file_id = message["photo"][-1]["file_id"]
                        image_cache[chat_id] = download_file(file_id)

                        buttons = [
                            [{"text": "Полутоновое изображение", "callback_data": "gr"},
                             {"text": "Пикселизировать", "callback_data": "px"}]
                        ]
                        send_message_with_buttons(chat_id,
                                                  "Выберите способ обработки:",
                                                  buttons)

                    else:
                        send_message_with_buttons(chat_id,
                                                  "Пожалуйста, отправьте изображение.",
                                                  [])

                elif callback_query:
                    chat_id = callback_query["message"]["chat"]["id"]
                    data = callback_query["data"]

                    if chat_id in image_cache:
                        input_image = image_cache[chat_id]

                        if data == "px":
                            print("g")
                            processed_image = replace_colors(input_image, colors.get('colors1'))
                            send_photo(chat_id, processed_image)
                            processed_image = replace_colors(input_image, colors.get('colors2'))
                            send_photo(chat_id, processed_image)
                            processed_image = replace_colors(input_image, colors.get('colors3'))
                            send_photo(chat_id, processed_image)
                        elif data == "gr":
                            processed_image = halftone_effect(input_image)
                            send_photo(chat_id, processed_image)
                    else:
                        send_message_with_buttons(chat_id,
                                                  "Нет изображения для обработки. "
                                                  "Пожалуйста, отправьте новое.",
                                                  [])


if __name__ == "__main__":
    main()
