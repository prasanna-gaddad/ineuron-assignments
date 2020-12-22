import os
import time
import requests
from selenium import webdriver

Driver = './chromedriver.exe'
search = 'cat'
number_image = 10


def search_and_download(Driver, search, number_image=10):
    folder_name = os.path.join('./images', "_".join(search.lower().split(' ')))

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with webdriver.Chrome(executable_path=Driver) as WD:

        res = fetch_image_urls(search, number_image, WD, intervel_beyween_interaction=0.5)

    counter = 0
    for elem in res:
        save_images(folder_name, elem, counter)
        counter += 1


def fetch_image_urls(search, number_image, WD, intervel_beyween_interaction):
    def scroll_to_end(WD):
        WD.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(intervel_beyween_interaction)

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={s}&oq={s}&gs_l=img"

    WD.get(search_url.format(s=search))

    image_urls = set()
    image_count = 0
    results_start = 0

    while number_image > image_count:
        scroll_to_end(WD)

        image_result = WD.find_elements_by_css_selector("img.Q4LuWd")  # urls stored
        number_of_image = len(image_result)

        print(f"Found: {number_of_image} search results. Extracting links from {results_start}:{number_of_image}")

        for img in image_result[results_start: number_of_image]:
            try:
                img.click()
                time.sleep(intervel_beyween_interaction)
            except Exception:
                continue

            actual_imgs = WD.find_elements_by_css_selector('img.n3VNCb')
            for actual_img in actual_imgs:
                if actual_img.get_attribute('src') and 'http' in actual_img.get_attribute('src'):
                    image_urls.add(actual_img.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= number_image:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                WD.execute_script("document.querySelector('.mye4qd').click();")

        results_start = len(image_result)

    return image_urls


def save_images(folder_name, elem, counter):
    try:
        image_content = requests.get(elem).content

    except Exception as e:
        print(f"ERROR - Could not download {elem} - {e}")

    try:
        f = open(os.path.join(folder_name, 'jpg' + "_" + str(counter) + '.jpg'), 'wb')
        f.write(image_content)
        f.close()
        print(f'SUCCESS - SAVED {elem} - as {folder_name}')

    except Exception as e:
        print(f"ERROR - Could not save {elem} - {e}")


search_and_download(Driver, search, number_image)
