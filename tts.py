import requests
import logging
import random
import mmap
import tqdm
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
                    logging.info("Key: " + str(keys[0]))
                    return keys[0]
            except Exception as e:
                logging.debug("TextToSpeech: get_key: exception: " + str(e))

        logging.error("TextToSpeech: get_key: No keys found")
        return None

    @staticmethod
    def get_speech_url(text: str,
                       lang: str = Lang.russian,
                       speaker: str = Voice.Female.oksana,
                       emotion: str = Emotion.neutral,
                       fmt: str = 'mp3') -> object:

        if TextToSpeech.key is not None:
            tts_key = TextToSpeech.key
        else:
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

    @staticmethod
    def get_sound_from_url(sound_url):

        attempts = 5
        proxy_list = get_proxies()

        while attempts > 0:

            attempts -= 1

            proxies = {
                'https': 'http://' + proxy_list[random.randint(0, len(proxy_list))],
            }

            logging.info("Proxy used: " + str(proxies))
            try:
                logging.info("Downloading sound...")
                data = requests.get(sound_url, proxies=proxies)
                return data.content
            except Exception as e:
                logging.debug("TextToSpeech: get_sound_from_url: request exception " + str(e))
        return None

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


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


def convert_file_to_sound(filename):
    with open(filename + ".txt", encoding='cp1251') as input:
        with open(filename + ".mp3", 'wb') as output:
            for line in tqdm.tqdm(input, total=get_num_lines(filename + ".txt")):
                if len(line) > 2000:
                    phrases = line.split(".")
                else:
                    phrases = [line]
                for phrase in phrases:
                    print("Working with phrase: " + phrase)
                    url = TextToSpeech.get_speech_url(phrase,
                                                      emotion=TextToSpeech.Emotion.neutral,
                                                      speaker=TextToSpeech.Voice.Female.oksana)
                    sound = TextToSpeech.get_sound_from_url(url)
                    output.write(sound)

convert_file_to_sound("mars")