import requests
import logging
import random
import mmap
import tqdm
import re


class TextToSpeech:

    # Docs: https://tech.yandex.ru/speechkit/cloud/doc/guide/common/speechkit-common-tts-http-request-docpage/

    def __init__(self):
        self.key = self.get_key() #"bf4277fc-06c0-405a-b278-b796bbbd3f27"
        self.net = self.Network()

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
                    data = requests.get(url, proxies=proxies)
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
            try:
                page = self.net.make_request(translate_url).text
                keys = re.findall(r"SPEECHKIT_KEY: '(.*)'", page)
                if len(keys) > 0:
                    logging.info("Key found: " + str(keys[0]))
                    return keys[0]
            except Exception as e:
                logging.debug("TextToSpeech: get_key: exception: " + str(e))

        logging.error("TextToSpeech: get_key: No keys found")
        return None

    def get_speech_url(self,
                       text: str,
                       lang: str = Lang.russian,
                       speaker: str = Voice.Female.oksana,
                       emotion: str = Emotion.neutral,
                       fmt: str = 'mp3') -> object:

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
    with open(filename + ".txt", encoding='cp1251') as input:
        with open(filename + ".mp3", 'wb') as output:
            for line in tqdm.tqdm(input, total=get_num_lines(filename + ".txt")):
                if len(line) > 2000:
                    phrases = line.split(".")
                else:
                    phrases = [line]
                for phrase in phrases:
                    print("Working with phrase: " + phrase)
                    if len(phrase.strip()) < 1:
                        print("Empty")
                        continue
                    url = tts.get_speech_url(phrase,
                                             emotion=TextToSpeech.Emotion.neutral,
                                             speaker=TextToSpeech.Voice.Female.oksana)
                    sound = tts.get_sound_from_url(url)
                    output.write(sound)
                    print("Done")


def main():
    logging.basicConfig(level=logging.INFO)
    convert_file_to_sound("mars")



if __name__ == "__main__":
    main()