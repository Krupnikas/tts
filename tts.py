import requests
import logging
import random
import re


class TextToSpeech:

    key = "bf4277fc-06c0-405a-b278-b796bbbd3f27"

    # Docs: https://tech.yandex.ru/speechkit/cloud/doc/guide/common/speechkit-common-tts-http-request-docpage/

    class Voice:

        class Male:
            zahar = "zahar"
            ermil = "ermil"

        class Female:
            jane = 'jane'
            oksana = 'oksana'
            alyss = 'alyss'
            omazh = 'omazh'

    class Emotion:
        good = "good"           # радостный, доброжелательный;
        evil = "evil"           # раздраженный;
        neutral = "neutral"     # нейтральный.

    # class Format:

    class Lang:
        russian = "ru-RU"       # русский
        english = "en-US"       # английский
        ukrain = "uk-UK"        # украинский
        turkish = "tr-TR"       # турецкий

    @staticmethod
    def get_key():
        translate_url = "https://translate.yandex.com/"

        attempts = 5
        proxy_list = get_proxies()

        while attempts > 0:

            attempts -= 1

            proxies = {
                'https': 'http://' + proxy_list[random.randint(0, len(proxy_list))],
            }

            print("Proxy used: ", proxies)
            try:
                page = requests.get(translate_url, proxies=proxies).text
                keys = re.findall(r"SPEECHKIT_KEY: '(.*)'", page)
                if len(keys) > 0:
                    return keys[0]
            except Exception as e:
                logging.debug("TextToSpeech: get_key: request exception " + str(e))

        logging.error("TextToSpeech: get_key: No keys found")
        return None

    @staticmethod
    def get_speech_url(text: str,
                       lang: str = Lang.russian,
                       speaker: str = Voice.Male.zahar,
                       emotion: str = Emotion.good,
                       fmt: str = 'mp3') -> object:

        tts_key = TextToSpeech.get_key()
        tts_url = f'https://tts.voicetech.yandex.net/generate' \
                  f'?text={text}' \
                  f'&format={fmt}' \
                  f'&lang={lang}' \
                  f'&speaker={speaker}' \
                  f'&emotion={emotion}' \
                  f'&key={tts_key}'

        #speed
        #
        return tts_url

def get_proxies():
    proxies_url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"
    data = requests.get(proxies_url)
    lines = data.text.splitlines()[4:-2]
    proxies = []
    for line in lines:
        if "-S" in line:
            proxy = line.split(" ")[0]
            proxies.append(proxy)

    return proxies


# print(get_proxies())
# print(TextToSpeech.get_speech_url("Привет, Стас!", emotion=TextToSpeech.Emotion.good))
import time
for i in range(3):
    time.sleep(1.32)
    print(TextToSpeech.get_key())