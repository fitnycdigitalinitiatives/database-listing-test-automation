#!/usr/bin/env python

import os
import json
import requests
from git import Repo
from git import Git
from config import lib_apps_key

endpoint = "https://lgapi-us.libapps.com/1.1/assets"
params = {
    "site_id": "942",
    "key": lib_apps_key,
    "asset_types": "10",
    "expand": "permitted_uses,az_types,az_props,subjects,icons",
}
ssh_private_key_path = os.path.expanduser('~/.ssh/id_ed25519')

# Construct the SSH command
ssh_cmd = f"ssh -i {ssh_private_key_path} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

proxy = "https://libproxy.fitsuny.edu/login?url="

base_directory = os.path.expanduser(
    "~/Desktop/repositories/database-listing-test-automation")

databases = requests.get(endpoint, params=params).json()

# add proxy here so that if it ever changes can be updated here rather than in javascript
for index, database in enumerate(databases):
    if database["meta"]["enable_proxy"]:
        databases[index]["url"] = proxy + databases[index]["url"]
    if "icons" in database:
        for icon in database["icons"]:
            if icon["id"] == 34462:
                database["enable_trial"] = True
            if icon["id"] == 34479:
                database["enable_new"] = True

# remove hidden items
clean_databases = []
for database in databases:
    if database["enable_hidden"] == False:
        clean_databases.append(database)

filename = os.path.join(base_directory, "page/databases.json")
with open(filename, "w") as outfile:
    json.dump(clean_databases, outfile, indent=4)

repo = Repo(base_directory)
repo.git.add(A=True)
repo.index.commit("Automated database update.")

# with Git().custom_environment(GIT_SSH_COMMAND=ssh_cmd):
origin = repo.remote(name='origin')
origin.push()
