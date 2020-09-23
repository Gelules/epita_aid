#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import wget
import git
import os
import time
import getpass


# Dirty hack
def page_is_loaded(browser, type_of_files):
    if type_of_files == "projects":
        for git_links in browser.find_elements_by_tag_name("input"):
            git_link = git_links.get_attribute("value")
            if git_link.startswith("git@"):
                return True

    if type_of_files == "documents":
        for links in browser.find_elements_by_tag_name("a"):
            link = links.get_attribute("href")
            if link.startswith("https://ceph.assistants.epita.fr/"):
                return True

    return False


def rows(browser):
    while True:
        try:
            rows_button = browser.find_element_by_id("pagination-next")
            res = rows_button.click()
        except Exception as e:
            return False
        else:
            return True


def connection():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    browser = webdriver.Firefox()
    url = "https://intra.assistants.epita.fr"
    browser.get(url)
    username_form = None
    while username_form is None:
        try:
            username_form = browser.find_element_by_id("id_username")
        except Exception as e:
            pass
    password_form = browser.find_element_by_id("id_password")
    username_form.send_keys(username)
    password_form.send_keys(password)
    submit_button = browser.find_element_by_class_name("mt-4")
    submit_button.click()
    return browser


def get_documents(browser):
    if not os.path.isdir("documents"):
        os.mkdir("documents")
    os.chdir("documents")

    browser.get("https://intra.assistants.epita.fr/documents")

    while not page_is_loaded(browser, "documents"):
        continue

    for links in browser.find_elements_by_tag_name("a"):
        link = links.get_attribute("href")
        if link.startswith("https://ceph.assistants.epita.fr/") and not os.path.exists(wget.filename_from_url(link)):
            wget.download(link)

    print()
    os.chdir("../")


def get_project(browser, project, to_git=False):
    name = project.rpartition("/")[-1]
    if name.startswith("exam"):
        return

    if not os.path.isdir(name):
        os.mkdir(name)
    os.chdir(name)

    browser.get(project)
    while not page_is_loaded(browser, "projects"):
        continue

    for links in browser.find_elements_by_tag_name("a"):
        link = links.get_attribute("href")
        if link.startswith("https://ceph.assistants.epita.fr/") and not os.path.exists(wget.filename_from_url(link)):
            wget.download(link)
    while rows(browser) is True:
        for links in browser.find_elements_by_tag_name("a"):
            link = links.get_attribute("href")
            if link.startswith("https://ceph.assistants.epita.fr/") and not os.path.exists(wget.filename_from_url(link)):
                if link.count('.') == 8:
                    os.system(f"wget '{link}'")
                else:
                    wget.download(link)

    if to_git:
        for git_links in browser.find_elements_by_tag_name("input"):
            git_link = git_links.get_attribute("value")
            if git_link.startswith("git@"):
                git.Git(".").clone(git_link)

    os.chdir("../")


def get_projects(browser):
    if not os.path.isdir("projects"):
        os.mkdir("projects")
    os.chdir("projects")

    browser.get("https://intra.assistants.epita.fr/projects")
    time.sleep(5)
    projects = []
    to_git = None

    while True:
        try:
            load_button = browser.find_element_by_class_name("MuiButton-outlined")
            load_button.click()
        except Exception as NoMoreButton:
            print("Can't load anymore : {}".format(NoMoreButton))
            break
        else:
            time.sleep(3)

    for links in browser.find_elements_by_tag_name("a"):
        link = links.get_attribute("href")
        if link.startswith("https://intra.assistants.epita.fr/projects/"):
            projects.append(link)

    while to_git is not True and to_git is not False:
        answer = input("git clone the projects? [y/n]: ")
        if answer == "y":
            to_git = True
        if answer == "n":
            to_git = False

    for project in projects:
        get_project(browser, project, to_git)


browser = connection()
get_documents(browser)
get_projects(browser)
browser.quit()
