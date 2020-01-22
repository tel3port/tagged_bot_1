from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import csv
import globals as gls
import glob
from random import randint
import hashlib
import requests
import os
import traceback
import schedule
import time
from PIL import Image
import io


class MainTaggedBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-sgm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--start-maximized")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # self.driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        self.login()

    def login(self):
        print("logging me in....")
        self.driver.get(gls.login_url)
        self.driver.maximize_window()
        email_xpath = '//*[contains(@name,"username")]'
        pw_xpath = '//*[contains(@name,"password")]'
        sign_in_btn_xpath = '//*[contains(@id,"submit_button")]'

        time.sleep(5)

        # click login button
        try:
            # fill up the credential fields
            self.driver.find_element_by_xpath(pw_xpath).send_keys(self.password)
            time.sleep(5)
            self.driver.find_element_by_xpath(email_xpath).send_keys(self.username)
            self.driver.find_element_by_xpath(sign_in_btn_xpath).click()

            print("login success...")
        except Exception as e:
            print("the login issue is: ", e)
            print(traceback.format_exc())
            pass

    # -------------------- user link extractor and saver section -----------------------------------------------------------------------

    @staticmethod
    def append_to_csv(saved_links_list, my_csv):
        try:
            this_csv = open(my_csv, gls.append)
            csv_writer = csv.writer(this_csv)
            for one_link in saved_links_list:
                csv_writer.writerow([str(one_link)])
                print("row (hopefully) written into csv")

        except Exception as em:
            print('append_to_csv Error occurred ' + str(em))
            print(traceback.format_exc())
            pass

        finally:
            print(" append_to_csv() done")

            pass

    @staticmethod
    def read_links_from_csv(my_csv):
        list_of_links = []
        try:
            with open(my_csv, gls.read) as rdr:
                reader = csv.reader(rdr, delimiter=",")
                for single_row in reader:
                    list_of_links.append(single_row)

        except IOError as x:
            print("read_links_from_csv problem reading the user_accounts csv", x)
            print(traceback.format_exc())
            pass

        except Exception as e:
            print("read_links_from_csv the problem is: ", e)
            print(traceback.format_exc())
            pass

        finally:
            print("number of links: ", len(list_of_links))
            return list_of_links

    @staticmethod
    def read_complements_from_csv(my_csv):
        list_of_complements = []
        try:
            with open(my_csv, gls.read) as rdr:
                reader = csv.reader(rdr, delimiter=",")
                for single_row in reader:
                    list_of_complements.append(single_row)

        except IOError as x:
            print("read_complements_from_csv problem", x)
            print(traceback.format_exc())
            pass

        except Exception as e:
            print("read_complements_from_csv the problem is: ", e)
            print(traceback.format_exc())
            pass

        finally:
            print("number of comps: ", len(list_of_complements))
            return list_of_complements

    def scrape_users(self):
        links_set = set()

        try:
            for i in range(5):
                time.sleep(7)
                self.driver.get(f'{gls.user_url_source}{i}')

                time.sleep(5)
                results = self.driver.find_elements_by_xpath('//a[@href]')

                print(f"number of pin links {len(results)}")

                for res in results:
                    final_link = res.get_attribute('href')
                    if 'www.tagged.com/browse/' in final_link and 'filters' not in final_link:
                        links_set.add(final_link)

        except Exception as we:
            print('scrape_users Error occurred ' + str(we))
            print(traceback.format_exc())
            pass
        finally:
            if len(links_set) > 0:
                self.append_to_csv(list(links_set), gls.user_urls_csv)
            else:
                pass

    # -------------------- image downloader section -----------------------------------------------------------------------

    def follow_and_dm_single_user(self, user_link, s_comp, random_lander):
        print("follow_and_dm_single_user started")
        time.sleep(7)
        try:
            self.driver.get(user_link)

            friend_button_xpath = '//*[contains(@id,"add-friend-button")]'
            message_btn_xpath = '//*[contains(@id,"message-button")]'
            dm_textbox_xpath = '//*[contains(@id,"im_input")]'
            send_btn_xpath = '//*[contains(@id,"im_send_button")]'

            friend_element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, friend_button_xpath)))
            time.sleep(15)

            friend_element.click()
            print(f"{user_link} friend requested!")
            time.sleep(7)

            current = self.driver.current_window_handle
            message_element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, message_btn_xpath)))
            message_element.click()
            time.sleep(5)

            new_tab = [tab for tab in self.driver.window_handles if tab != current][0]
            self.driver.switch_to.window(new_tab)
            self.driver.find_element_by_xpath(dm_textbox_xpath).send_keys(f'{s_comp[0]}. What do you think of this? Is it legit? {random_lander}')
            time.sleep(5)
            self.driver.find_element_by_xpath(send_btn_xpath).click()

            print(f"single dm sent to {user_link}")

            self.driver.close()
            time.sleep(5)

            self.driver.switch_to.window(current)
            print("follow_and_dm_single_user finished")

        except Exception as e:
            print("follow_DM_single_user the problem is: ", e)
            print(traceback.format_exc())
            pass

        # close the tab
        finally:
            pass

    def status_updater_text(self, homepage_link, single_update, single_lander):
        print("starting text status update")
        try:
            self.driver.get(homepage_link)

            status_textbox_xpath = '//*[contains(@placeholder,"you doing today?")]'
            post_btn_xpath = '//*[contains(@ng-click,"postStatus()")]'

            self.driver.execute_script("window.scrollBy(0,500)", "")
            time.sleep(10)

            self.driver.find_element_by_xpath(status_textbox_xpath).send_keys(f'{single_update[0]} {single_lander}')
            time.sleep(5)
            self.driver.find_element_by_xpath(post_btn_xpath).click()

            print("text status update done")

        except Exception as e:
            print("the status_updater_text issue is: ", e)
            print(traceback.format_exc())
            pass

    def status_updater_image(self, homepage_link, single_image):
        print("image status update started")

        try:
            self.driver.get(homepage_link)

            time.sleep(7)
            self.driver.execute_script("window.scrollBy(0,400)", "")
            time.sleep(10)

            self.driver.find_element_by_id('photoUpload').send_keys(f"{os.getcwd()}{'/'}{single_image}")

            time.sleep(7)
            print("image status update done")

        except Exception as e:
            print("the status_updater_image issue is: ", e)
            print(traceback.format_exc())
            pass

    def user_status_liker_commenter(self):
        pass

    # -------------------- image downloader section -----------------------------------------------------------------------

    @staticmethod
    def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
        def scroll_to_end(wd):
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleep_between_interactions)

            # build the google query

        # build the google query
        search_url = 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img'

        time.sleep(12)

        # open tab
        # current = wd.current_window_handle
        # wd.execute_script("window.open();")
        # new_tab = [tab for tab in wd.window_handles if tab != current][0]
        # wd.switch_to.window(new_tab)
        # You can use (Keys.CONTROL + 't') on other OSs
        # load the page
        time.sleep(12)
        wd.get(search_url.format(q=query))

        image_urls = set()
        image_count = 0
        results_start = 0
        while image_count < max_links_to_fetch:
            scroll_to_end(wd)

            # get all image thumbnail results
            thumbnail_results = wd.find_elements_by_css_selector("img.rg_ic")
            number_results = len(thumbnail_results)

            print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

            for img in thumbnail_results[results_start:number_results]:
                # try to click every thumbnail such that we can get the real image behind it
                try:
                    img.click()
                    time.sleep(sleep_between_interactions)
                except Exception as e:
                    print("the problem is, ", str(e))
                    continue

                # extract image urls
                actual_images = wd.find_elements_by_css_selector('img.irc_mi')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src'):
                        image_urls.add(actual_image.get_attribute('src'))

                image_count = len(image_urls)

                if len(image_urls) >= max_links_to_fetch:
                    print(f"Found: {len(image_urls)} image links, done!")
                    break
            else:
                print("Found:", len(image_urls), "image links, looking for more ...")
                time.sleep(1)
                load_more_button = wd.find_element_by_css_selector(".ksb")
                if load_more_button:
                    wd.execute_script("document.querySelector('.ksb').click();")

            # move the result startpoint further down
            results_start = len(thumbnail_results)

            # # close the tab
            # wd.close()
            #
            # wd.switch_to.window(current)

        return image_urls

    @staticmethod
    def persist_image(folder_path: str, url: str):
        try:
            image_content = requests.get(url).content

        except Exception as e:
            print(f"ERROR - Could not download {url} - {e}")
            pass

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            print(f"SUCCESS - saved {url} - as {file_path}")
        except Exception as e:
            print(f"ERROR - Could not save {url} - {e}")
            pass

    def search_and_download(self, search_term: str, driver_path: str, target_path='./dld_images', number_images=5):
        target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
        target_folder = './dld_images'
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # with webdriver.Chrome(executable_path=driver_path) as wd:
        res = self.fetch_image_urls(search_term, number_images, wd=self.driver, sleep_between_interactions=0.5)

        for elem in res:
            self.persist_image(target_folder, elem)

# -------------------- image optimiser section -----------------------------------------------------------------------

    @staticmethod
    def image_optimiser():
        try:
            raw_image_list = glob.glob('dld_images/*')
            print(f'number of images: {len(raw_image_list)}')

            count = 0
            for single_image in raw_image_list:
                print(f'processing {single_image}...')
                image = Image.open(single_image)
                new_image = image.resize((500, 300))
                new_image.save(f'./media/{"final_img_"}{count}.jpg')
                count += 1

            print(" image optimisation done")

        except Exception as we:
            print('image_optimiser Error occurred ' + str(we))
            print(traceback.format_exc())
            pass

    # -------------------- image refresher section -----------------------------------------------------------------------

    @staticmethod
    def image_deleter():
        try:
            for i in glob.glob("./dld_images/*.jpg"):
                os.remove(i)

        except Exception as we:
            print('image_deleter Error occurred ' + str(we))
            print(traceback.format_exc())
            pass

    # -------------------- dyno restart section -----------------------------------------------------------------------

    @staticmethod
    def exit_application():
        exit(143)

    # -------------------- bot's entry point -----------------------------------------------------------------------


if __name__ == "__main__":
    is_running = True

    tagged_bot = MainTaggedBot("2ksaber@gmail.com", "8GgqbBcGp@Nx4#G")

    # refreshes images 3 times a week
    def image_refresh_sequence():
        print("starting image refresh")
        list_of_search_terms = ["cute cat phone wallpaper", "cute puppy phone wallpaper", "cute pet phone wallpaper", "cute kitten phone wallpaper", "cute lion phone wallpaper", "cute elephant phone wallpaper",
                                " cute dog phone wallpaper", 'fluffy sweater phone wallpaper', "cute bird phone wallpaper", "cute calf phone wallpaper"]
        random_search_term = list_of_search_terms[randint(0, len(list_of_search_terms) - 1)]
        time.sleep(5)
        try:
            tagged_bot.search_and_download(random_search_term, './chromedriver', './dld_images', 35)
            time.sleep(10)
            tagged_bot.image_optimiser()
            tagged_bot.image_deleter()
            print("image refresh done for today")

        except Exception as we:
            print('image_refresh_sequence Error occurred ' + str(we))
            print(traceback.format_exc())
            pass

    def tagged_actions_sequence():
        for i in range(50):
            print(f"tagged action sequence running loop num: {i}")

            complement_list = tagged_bot.read_complements_from_csv(gls.complements_csv)
            single_comp = complement_list[randint(0, len(complement_list) - 1)]
            static_user_url_list = tagged_bot.read_links_from_csv(gls.user_urls_csv)
            single_user_url = static_user_url_list[randint(0, len(static_user_url_list) - 1)]
            image_list = glob.glob('media/*')
            tagged_bot.follow_and_dm_single_user(user_link=single_user_url[0], s_comp=single_comp, random_lander=gls.single_lander_source())

            time.sleep(randint(10, 20))

            tagged_bot.status_updater_text(gls.status_home_page, complement_list[randint(0, len(complement_list) - 1)], gls.single_lander_source())

            time.sleep(randint(10, 20))

            tagged_bot.status_updater_image(gls.status_home_page, image_list[randint(0, len(image_list) - 1)])
            time.sleep(randint(10, 20))

    def user_scraper_sequence():
        tagged_bot.scrape_users()  # from web and saves to csv

    # def runner_true():
    #     global is_running
    #     is_running = True
    #     print("runner set to true")
    #
    # def runner_false():
    #     global is_running
    #     is_running = False
    #     print("runner set to false")

    def custom_tagged_bot_1_scheduler():
        try:
            print("starting custom scheduler")
            schedule.every().day.at("12:30").do(tagged_bot.exit_application)
            schedule.every().day.at("01:03").do(image_refresh_sequence)
            schedule.every().day.at("02:03").do(tagged_bot.exit_application)
            schedule.every().day.at("03:13").do(tagged_actions_sequence)
            schedule.every().day.at("04:33").do(tagged_actions_sequence)
            schedule.every().day.at("05:25").do(tagged_actions_sequence)
            schedule.every().day.at("06:44").do(tagged_bot.exit_application)
            schedule.every().day.at("07:35").do(tagged_actions_sequence)
            schedule.every().day.at("08:33").do(tagged_actions_sequence)
            schedule.every().day.at("09:35").do(tagged_actions_sequence)
            schedule.every().day.at("10:35").do(tagged_actions_sequence)
            schedule.every().day.at("11:30").do(tagged_bot.exit_application)
            schedule.every().day.at("12:35").do(tagged_actions_sequence)
            schedule.every().day.at("13:33").do(tagged_actions_sequence)
            schedule.every().day.at("14:35").do(tagged_actions_sequence)
            schedule.every().day.at("15:35").do(tagged_actions_sequence)
            schedule.every().day.at("16:30").do(tagged_bot.exit_application)
            schedule.every().day.at("17:35").do(tagged_actions_sequence)
            schedule.every().day.at("18:33").do(tagged_actions_sequence)
            schedule.every().day.at("19:34").do(tagged_actions_sequence)
            schedule.every().day.at("20:40").do(tagged_actions_sequence)
            schedule.every().day.at("21:52").do(tagged_actions_sequence)
            schedule.every().day.at("22:30").do(tagged_bot.exit_application)


            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as e:
            print('custom_tagged_bot_1_scheduler Error occurred ' + str(e))
            print(traceback.format_exc())
            pass


    custom_tagged_bot_1_scheduler()


    # def run_locally():
    #     for _ in range(5):
    #         tagged_actions_sequence()
    #         time.sleep(12)
    #         image_refresh_sequence()
    #         time.sleep(7)

    # run_locally()
