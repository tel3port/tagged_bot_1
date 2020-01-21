from random import randint
import time

complements_csv = "complements.csv"
status_updates_csv = "tagged_status_updates.csv"
user_urls_csv = 'tagged_user_urls.csv'

write = 'w'
read = "r"
append = 'a'
login_url = "https://secure.tagged.com/secure_login.html?ver=2&loc=en_US&uri=http%3A%2F%2Fwww.tagged.com&display=full"
user_url_source = 'http://www.tagged.com/browse?page='
status_home_page = 'http://www.tagged.com/home.html?dataSource=Feed&=&jli=1#38;ll=nav'


def sleep_time():
    t = randint(7, 65)
    print(f"thread sleeping for {t} seconds...")

    time.sleep(t)

    return t


def single_lander_source():
    list_of_landers = ['https://cool-giveaways.weebly.com/',
                       'https://win-150-dollars-now.weebly.com/',
                       'https://freebie-heaven.weebly.com/',
                       'https://win-google-pixel-now.weebly.com/',
                       'https://win-nintendo-switch-now.weebly.com/',
                       'https://win-a-fortune-today.weebly.com/',
                       'https://amzn.to/379FhAY'
                       ]

    return list_of_landers[randint(0, len(list_of_landers) - 1)]
