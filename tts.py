import requests
import logging
import random
import mmap
from tqdm import tqdm
from threading import Thread
import re
from time import sleep


class TextToSpeech:

    # Docs: https://tech.yandex.ru/speechkit/cloud/doc/guide/common/speechkit-common-tts-http-request-docpage/

    def __init__(self):
        self.net = self.Network()
        self.key = self.get_key() #"bf4277fc-06c0-405a-b278-b796bbbd3f27"

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

    class Network(object):

        proxy_list = []

        def update_proxy_list(self):
            proxies_url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"
            data = requests.get(proxies_url)
            lines = data.text.splitlines()[4:-2]
            self.proxy_list = []
            for line in lines:
                if "-S" in line:  # Getting only https proxy
                    proxy = line.split(" ")[0]
                    self.proxy_list.append(proxy)

        def make_request(self, url, attempts=5):

            if len(self.proxy_list) == 0:
                self.update_proxy_list()

            if len(self.proxy_list) == 0:
                logging.warning("Can't get proxy list. Using my ip")

            while attempts > 0:

                attempts -= 1

                proxies = {
                    'https': 'http://' + self.proxy_list[random.randint(0, len(self.proxy_list))],
                }

                logging.debug("Proxy used: " + str(proxies))
                try:
                    logging.debug("Making request...")
                    data = requests.get(url, proxies=proxies, timeout=10)
                    logging.debug("Request done")
                    return data
                except Exception as e:
                    logging.debug("Network: request exception " + str(e))
            return None

    def get_key(self):
        translate_url = "https://translate.yandex.com/"

        attempts = 5

        while attempts > 0:
            attempts -= 1
            logging.info("Getting key...")
            try:
                page = self.net.make_request(translate_url).text
                keys = re.findall(r"SPEECHKIT_KEY: '(.*)'", page)
                if len(keys) > 0:
                    logging.info("Key found: " + str(keys[0]))
                    return keys[0]
            except Exception as e:
                logging.warning("TextToSpeech: get_key: exception: " + str(e))

        logging.error("TextToSpeech: get_key: No keys found")
        return None

    def get_speech_url(self,
                       text: str,
                       lang: str = Lang.russian,
                       speaker: str = Voice.Female.oksana,
                       emotion: str = Emotion.neutral,
                       fmt: str = 'mp3') -> object:

        if self.key is None:
            logging.error("Empty key field")
            return None

        tts_url = f'https://tts.voicetech.yandex.net/generate' \
                  f'?text={text}' \
                  f'&format={fmt}' \
                  f'&lang={lang}' \
                  f'&speaker={speaker}' \
                  f'&emotion={emotion}' \
                  f'&key={self.key}'

        #speed
        #
        return tts_url

    def get_sound_from_url(self, sound_url):

        attempts = 5

        if sound_url is None:
            logging.error("Wrong sound url")
            return None

        while attempts > 0:
            try:
                logging.info("Downloading sound...")
                data = self.net.make_request(sound_url)
                logging.info("Downloading sound done")
                return data.content
            except Exception as e:
                logging.debug("TextToSpeech: get_sound_from_url: request exception " + str(e))
        return None


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


def convert_file_to_sound(filename):
    tts = TextToSpeech()
    threads = {}
    sounds = {}
    input_index = 0
    output_index = 0

    max_working_threads = 10
    max_threads = 100

    def converter(phrase, index):
        logging.info("Working with phrase: " + phrase[:-1])
        url = tts.get_speech_url(phrase,
                                 emotion=TextToSpeech.Emotion.neutral,
                                 speaker=TextToSpeech.Voice.Female.oksana)

        sound = tts.get_sound_from_url(url)
        sounds[index] = sound
        logging.info("Phrase " + str(index) + " converted")

    def save_results(file):
        nonlocal output_index
        logging.info(f"Threads: {len(threads)}, sounds: {len(sounds)}.")
        if output_index not in sounds.keys():
            logging.info(f"Phrase {output_index} is not ready. Waiting...")
            return
        logging.info("Writing to file...")
        while output_index in sounds.keys():
            threads[output_index].join()
            file.write(sounds[output_index])
            sounds.__delitem__(output_index)
            threads.__delitem__(output_index)
            output_index += 1
        logging.info("Done")

    with open(filename + ".txt", encoding='cp1251') as input:
        with open(filename + ".mp3", 'wb') as output:
            for line in tqdm(input, total=get_num_lines(filename + ".txt")):
                if len(line) > 2000:    # API limit
                    phrases = line.split(".")
                else:
                    phrases = [line]
                for phrase in phrases:
                    if len(phrase.strip()) < 1:
                        logging.debug("Empty phrase skipped")
                        continue

                    logging.info(f"Creating thread for phrase {phrase[:-1]}")
                    threads[input_index] = Thread(target=converter, args=(phrase, input_index))

                    while len(threads) - len(sounds) >= max_working_threads or len(threads) >= max_threads:
                        logging.info("Waiting for previous threads...")
                        save_results(output)
                        sleep(1)

                    threads[input_index].start()
                    input_index += 1

            while len(sounds) > 0:
                save_results(output)
                sleep(1)

            logging.info("Done")


def main():
    logging.basicConfig(level=logging.INFO)
    convert_file_to_sound("test")


if __name__ == "__main__":
    main()