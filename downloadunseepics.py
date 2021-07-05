# Author: Icarus Caeser
# Created at 3:38 PM on 05/07/21

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import urllib3
import shutil

import time
import base64
import os
import zipfile
import logging
from io import BytesIO
import shutil
import config


def zipdir(path) -> BytesIO:

    directory_name = os.path.basename(path)
    print('zipping directory {}'.format(directory_name))
    # ref https://stackoverflow.com/questions/27337013/how-to-send-zip-files-in-the-python-flask-framework

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                print(root + file)
                zipf.write(os.path.join(root, file), arcname=file)
    memory_file.seek(0)
    print('Deleting directory {}'.format(path))
    shutil.rmtree(path)
    return memory_file


def create_new_downloads_directory():
    directory2save = str(round(time.time()))
    directory2save = os.path.join(config.DOWNLOAD_DIR, directory2save)
    print('Create directory {}'.format(directory2save))
    os.mkdir(directory2save)

    return directory2save


class Unsee:

    def get_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--auto-open-devtools-for-tabs")
        if os.environ.get('staging'):
            driver = webdriver.Chrome(options=options, executable_path=config.CHROMEDRIVER_PATH)
        else:
            driver = webdriver.Chrome(options=options)
        return driver


class DownloadUnsee(Unsee):
    def __init__(self, unsee_url):
        self.url = unsee_url
        self.driver = None

    def download_pics(self):

        try:
            self.driver = self.get_driver()
            directory2save = create_new_downloads_directory()
            wait = WebDriverWait(self.driver, 15)
            self.driver.get(self.url)

            wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "grid")))
            images_element = self.driver.find_elements_by_id('images')[1]
            # give sometime for other images to load
            time.sleep(5)

            containers = images_element.find_elements_by_class_name('jss82')

            http = urllib3.PoolManager()
            for container in containers:
                try:
                    canvas_element = container.find_element_by_tag_name('img')
                    image_id = canvas_element.get_attribute('id')
                    image_location = os.path.join(directory2save, image_id + ".jpeg")
                    print("saving " + image_id + " as " + image_location)

                    #urllib.request.urlretrieve('https://unsee.cc/image?id=' + image_id + '&size=big', image_location)
                    with open(image_location, 'wb') as out:
                        r = http.request('GET', 'https://unsee.cc/image?id=' + image_id + '&size=big', preload_content=False)
                        shutil.copyfileobj(r, out)

                except Exception as exc:
                    print("Could not find the element")
                    print(exc)

            print("Done")
            self.driver.close()

            return zipdir(directory2save)

        except Exception as exc:
            self.driver.close()
            raise exc


class DownloadOldUnsee(Unsee):
    def __init__(self, url):
        self.url = url
        self.driver = None

    def convert_canvas_to_image(self, canvas_element):

        # get the canvas as a PNG base64 string
        canvas_base64 = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",
                                                   canvas_element)

        # decode
        canvas_png = base64.b64decode(canvas_base64)
        return canvas_png

    def download_pics(self):
        """
        Returns a zip object that can be sent back to client.
        """
        try:
            directory2save = create_new_downloads_directory()

            self.driver = self.get_driver()
            wait = WebDriverWait(self.driver, 30)
            self.driver.get(self.url)

            images_element = self.driver.find_element_by_id('images')
            # wait until at least one image is visible
            wait.until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "image_container")))
            # give sometime for other images to load
            time.sleep(10)

            containers = images_element.find_elements_by_class_name('image_container')

            for container in containers:
                try:
                    canvas_element = container.find_element_by_tag_name('canvas')
                    element_id = canvas_element.get_attribute('id')
                    canvas_image = self.convert_canvas_to_image(canvas_element)
                    image_location = os.path.join(directory2save, element_id + ".png")
                    print("saving " + element_id + "as " + image_location)

                    with open(image_location, 'wb') as image:
                        image.write(canvas_image)

                except Exception as exc:
                    print("Could not find the element")
                    print(exc)

            print("Done")
            self.driver.close()

            # zip the directory and return the same.
            return zipdir(directory2save)

        except Exception as exc:
            self.driver.close()
            raise exc

