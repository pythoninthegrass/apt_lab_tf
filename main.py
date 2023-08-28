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


def read_master_tf(master_file):
    file_access = open(master_file, "r")
    file_content = file_access.read()
    file_access.close()
    return file_content


def build_main(mgmt_ip):
    static_info = Path("./terraform/providers.tf").read_text()
    build_info = Path("./terraform/resources.tf").read_text()

    main_tf = open('./labs/main.tf', 'a+')
    static_info = static_info.replace('subid', subscription_id)
    static_info = static_info.replace('clid', client_id)
    static_info = static_info.replace('clse', client_secret)
    static_info = static_info.replace('tenid', tenant_id)
    main_tf.write(static_info)
    tmp = build_info
    tmp = tmp.replace('mgmtip', mgmt_ip[0])
    tmp = tmp.replace('regionalregion', region)
    main_tf.write(tmp)


def run_cmd(args):
    """Run command, transfer stdout/stderr back into this process's stdout/stderr"""
    print("Running command: %s" % " ".join(args))
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b''):
        print(line.decode('utf-8').rstrip())
    p.stdout.close()
    return p.wait()


def main():
    parser = argparse.ArgumentParser(
        description='Creates Azure resources for Lab environment with terraform'
    )
    parser.add_argument(
        '-m',
        help='Public IP Addresses for management access rules (ex. 1.1.1.1 or 1.1.1.0/24',
        metavar='input_mgmt', dest='mgmt_ip', type=str, nargs='+', required=True
    )
    parser.add_argument(
        '-d', '-destroy',
        help='Will use terraform Destroy to destroy everything created by this script in Azure', action='store_true', dest='destroy_switch', required=False
    )
    args=parser.parse_args()

    if args.destroy_switch:
        print("===This will use Terraform to DESTROY the Lab environment that was created in Azure======\nThis will 'un-build' the lab and all the data will be destroyed")
        time.sleep(3)
        cmd = ["cd", "labs", "&&", "terraform", "destroy"]
        run_cmd(cmd)
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

    mgmt_ip = args.mgmt_ip
    master_dir = "./master"
    class_dir = "./labs"
    copy(master_dir, class_dir)
    build_main(mgmt_ip)

    # TODO: test locally first
    # terraform init
    cmd = ["cd", "labs", "&&", "terraform", "init"]
    run_cmd(cmd)

    # terraform plan
    cmd = ["cd", "labs", "&&", "terraform", "plan", "-out=tfplan"]
    run_cmd(cmd)

    # terraform apply
    cmd = ["cd", "labs", "&&", "terraform", "apply", "-auto-approve"]
    run_cmd(cmd)


if __name__ == "__main__":
    main()
