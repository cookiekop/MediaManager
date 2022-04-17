import aria2p
from header import *


def main():
    aria2 = aria2p.API(
        aria2p.Client(
            host=settings['aria2_host'],
            port=settings['aria2_port'],
            secret=settings['aria2_secret']
        )
    )
    def download(type):
        with open("{}.magnets".format(type), "r") as f:
            for magnet in f:
                if len(aria2.get_downloads()) > settings['max_downloads']: break
                aria2.add_magnet(magnet, {'dir': "{}/{}".format(settings['download_dir'], type)})

    for type in ['movie', 'series']:
        download(type)

if __name__ == "__main__":
    main()