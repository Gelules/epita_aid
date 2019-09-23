#!/usr/bin/env python3

from selenium import webdriver
import wget
import git
import os
import time
import getpass


def connection():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    browser = webdriver.Firefox()
    browser.implicitly_wait(5)
    url = "https://cri.epita.fr/accounts/auth/login/?next=/oidc/authorize?scope=openid oidc profile email epita&state=V7xPGlGB3-9Y9iI0SLGwABmH2qxD_pjsmGFCJALknlU.sY2eNKviZ7M.acu-frontend&response_type=code&client_id=444246&redirect_uri=https://keycloak.assistants.epita.fr/auth/realms/assistants/broker/oidc-cri/endpoint&nonce=83788e40-dd27-429b-b818-6a98ce4e710b"
    browser.get(url)
    username_form = browser.find_element_by_id("id_username")
    password_form = browser.find_element_by_id("id_password")
    username_form.send_keys(username)
    password_form.send_keys(password)
    submit_button = browser.find_element_by_class_name("mdl-button")
    submit_button.click()
    return browser


def get_documents(browser):
    if not os.path.isdir("documents"):
        os.mkdir("documents")
    os.chdir("documents")
    
    browser.get("https://intra.assistants.epita.fr/documents")
    time.sleep(5)
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
    time.sleep(5)

    for links in browser.find_elements_by_tag_name("a"):
        link = links.get_attribute("href")
        if link.startswith("https://ceph.assistants.epita.fr/") and not os.path.exists(wget.filename_from_url(link)):
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
