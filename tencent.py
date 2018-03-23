from utils import open_driver, track_alert,get


def main():
    with open_driver() as driver:
        with track_alert(driver):
            get('http://ac.qq.com/MyComic')
            pass


if __name__ == '__main__':
    main()
