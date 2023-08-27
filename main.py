#!/usr/bin/env python3

import argparse
import errno
import os
import shutil
import subprocess
import time
from decouple import config
from pathlib import Path
# import urllib
# import json
# import configparser
# import csv
# from requests import get

"""
SETUP
    By default your VMs will be deployed to Azure Cloud in a Central US data center.
    For a list of valid, alternative locations run the following command:
        az account list-locations -o table

    Apply the desired value from the "name" column in the region variable.

    To deploy your VMs to Azure Cloud, you will first need to create an Azure
    Service Principal and a "secret token". These will be used by this script to
    Terraform your lab environment.
    See -> https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret

BEWARE
    The following information allows direct login to your Azure Cloud environment!
    Treat this file as highly confidential!
"""

region          = config('REGION', default='centralus')
subscription_id = config('SUBSCRIPTION_ID')
client_id       = config('CLIENT_ID')
client_secret   = config('CLIENT_SECRET')
tenant_id       = config('TENANT_ID')


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        elif e.errno == errno.EEXIST:
            shutil.rmtree(dest)
            shutil.copytree(src, dest)
        else:
            print('Directory not copied. Error: %s' % e)


def readmastertf(masterfile):
    fileaccess = open(masterfile, "r")
    filecontent = fileaccess.read()
    fileaccess.close()
    return filecontent


def buildmain(mgmtip):
    staticinfo = Path("static.tf").read_text()
    buildinfo = Path("build.tf").read_text()

    maintf = open('./labs/main.tf', 'a+')
    staticinfo = staticinfo.replace('subid', subscription_id)
    staticinfo = staticinfo.replace('clid', client_id)
    staticinfo = staticinfo.replace('clse', client_secret)
    staticinfo = staticinfo.replace('tenid', tenant_id)
    maintf.write(staticinfo)
    tmp = buildinfo
    tmp = tmp.replace('mgmtip', mgmtip[0])
    tmp = tmp.replace('regionalregion',region)
    maintf.write(tmp)


def main():
    parser = argparse.ArgumentParser(
        description='Creates Azure resources for Lab environment with terraform'
    )
    parser.add_argument(
        '-m',
        help='Public IP Addresses for management access rules (ex. 1.1.1.1 or 1.1.1.0/24',
        metavar='input_mgmt', dest='mgmtip', type=str, nargs='+', required=True
    )
    parser.add_argument(
        '-d', '-destroy',
        help='Will use terraform Destroy to destroy everything created by this script in Azure', action='store_true', dest='destroy_switch', required=False
    )
    args=parser.parse_args()

    if args.destroy_switch:
        print("===This will use Terraform to DESTROY the Lab environment that was created in Azure======\nThis will 'un-build' the lab and all the data will be destroyed")
        time.sleep(3)
        # os.system("cd labs && terraform destroy")
        cmd = ["cd", "labs", "&&", "terraform", "destroy"]
        subprocess.run(
            cmd,
            shell=False,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        # TODO: move to a global scope
        def split_args(arg):
            try:
                arg=" ".join(arg)
                arg=arg.replace(" ", "")
                if any("," in item for item in arg):
                    arg = arg.split(",")
                if type(arg) is list:
                    return arg
                else:
                    return [arg]
            except TypeError:
                return None

    mgmtip = args.mgmtip
    masterfolder = "./master"
    classfolder = "./labs"
    copy(masterfolder, classfolder)
    buildmain(mgmtip)
    # os.system("cd labs && terraform init")
    cmd = ["cd", "labs", "&&", "terraform", "init"]
    subprocess.run(
        cmd,
        shell=False,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # os.system("cd labs && terraform apply -auto-approve")
    cmd = ["cd", "labs", "&&", "terraform", "apply", "-auto-approve"]
    subprocess.run(
        cmd,
        shell=False,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


if __name__ == "__main__":
    main()
