import yaml
import datetime
import csv
import base64
import os
from pathlib import Path
from pyvas_handler import get_last_reports, download_report_as_csv

# DEBUG =  True
DEBUG = False

config_file_path = "config.yaml"  # path to config file
default_processed_reports_path = "last_processed_reports.csv"  # the default path to the last processed CSV File
default_csv_delimiter = ";"  # default delimiter used in the last processed CSV File
default_csv_quote_character = "|"  # default character used for comments in the last processed CSV File
default_save_directory = "../"  # default folder path to store the
configuration = {}

default_processed_reports = {
    "path": default_processed_reports_path,
    "csv-delimiter": default_csv_delimiter,
    "csv-quote-character": default_csv_quote_character
}

if DEBUG is False:
    print("""
       ___                __     ___    ____           
      / _ \ _ __   ___ _ _\ \   / / \  / ___|          
     | | | | '_ \ / _ \ '_ \ \ / / _ \ \___ \          
     | |_| | |_) |  __/ | | \ V / ___ \ ___) |         
      \___/| .__/ \___|_| |_|\_/_/   \_\____/          
           |_|                                         
                       ____                    
                      |___ \                   
                        __) |                  
                       / __/                   
                      |_____|                  
                                                   
      ____        __           _   ____        _       
     |  _ \  ___ / _| ___  ___| |_|  _ \  ___ (_) ___  
     | | | |/ _ \ |_ / _ \/ __| __| | | |/ _ \| |/ _ \ 
     | |_| |  __/  _|  __/ (__| |_| |_| | (_) | | (_) |
     |____/ \___|_|  \___|\___|\__|____/ \___// |\___/ 
                                            |__/     
                                                 by Konsti
    """)
    print("\n\n [+] OpenVAS2DefectDojo exports all new OpenVAS Reports from one\n [+] or multiple OpenVAS instances \
to the local system. Options \n [+] are defined in the config.yml file.\n")


def print_datetime(message="none"):
    print("\n [+] " + message + " -> " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")


print_datetime('Start')

if Path(config_file_path).is_file() is not True:
    print("No config file found")
    exit(1)

with open(config_file_path, "r") as f:
    try:
        configuration = yaml.load(f)
    except yaml.YAMLError as exc:
        print("Error while reading the config.yaml")
        print(exc)
        exit(1)

# Configure the missing parameter to default
if configuration['save-directory'] is None:
    configuration['save-directory'] = default_save_directory

if configuration["processed-reports"] is None:
    configuration["processed-reports"] = default_processed_reports

if configuration["processed-reports"]["path"] is None:
    configuration["processed-reports"]["path"] = default_processed_reports_path

if configuration["processed-reports"]["csv-delimiter"] is None:
    configuration["processed-reports"]["csv-delimiter"] = default_csv_delimiter

if configuration["processed-reports"]["csv-quote-character"] is None:
    configuration["processed-reports"]["csv-quote-character"] = default_csv_quote_character

# current datetime formatted for the last processed CSV File
reg_format_date = datetime.datetime.now().strftime(
    "%Y-%m-%d" +
    configuration["processed-reports"]["csv-delimiter"] +
    "%H:%M:%S"
)


def get_folder_path():
    if configuration['save-directory'][:-1] != "/":
        configuration['save-directory'] = configuration['save-directory'] + "/"
    if configuration['save-directory'][0] == "/":
        configuration['save-directory'] = "../" + configuration['save-directory']
    if Path(configuration['save-directory']).is_dir() is not True:
        os.mkdir(configuration['save-directory'])
    return configuration['save-directory']


if Path(configuration["processed-reports"]["path"]).is_file() is not True:
    with open(configuration["processed-reports"]["path"], "w+") as f:
        f.write(
            configuration["processed-reports"]["csv-delimiter"].join([
                "date",
                "time",
                "instance_name",
                "task_name",
                "task_id",
                "report_id",
                "scan_end",
                "timestamp",
                "scan_start",
                "false_positive",
                "debug",
                "hole",
                "warning",
                "info",
                "log",
                "severity"
            ]) + "\n"
        )

with open(configuration["processed-reports"]["path"], "r") as processed_reports_file:
    processed_reports = csv.reader(
        processed_reports_file,
        delimeter=configuration["processed-reports"]["csv-delimiter"],
        quotechar=configuration["processed-reports"]["csv-quote-character"]
    )

    for instance_name in configuration["openvas-instances"]:
        instance = configuration["openvas-instances"][instance_name]
        processed_instance_reports = []

        for row in processed_reports:
            if row[2] == instance_name.replace("-", "_"):
                processed_instance_reports.append({'task_id': row[4], 'report_id': row[5]})

        last_reports = get_last_reports(configuration["openvas-instances"][instance_name], processed_instance_reports)

        for report in last_reports:
            with open(
                    get_folder_path() +
                    instance_name.replace("-", "_") +
                    "-" +
                    report['task_name'].replace(" ", "_") +
                    "-" +
                    report['last_report']['@id'].replace("-", "_") +
                    "-" +
                    report['last_report']['scan_start']
                    .replace("-", "")
                    .replace(":", "")
                    .replace("Z", "")
                    .replace("T", "") +
                    ".csv",
                    "w+"
            ) as report_file:
                if DEBUG:
                    print(
                        base64.b64decode(
                            download_report_as_csv(report['last_report']['@id'], instance)
                        ).decode('utf-8')
                    )
                report_file.write(
                    base64.b64decode(
                        download_report_as_csv(report['last_report']['@id'], instance)
                    ).decode('utf-8')
                )

            with open(configuration["processed-reports"]["path"], "a") as f:
                # date;time;instance_name;task_name;task_id;report_id;scan_end;timestamp;scan_start;false_positive;debug;hole;warning;info;log;severity
                f.write(
                    configuration["processed-reports"]["csv-delimiter"].join([
                        reg_format_date,
                        instance_name.replace("-", "_"),
                        report['task_name'],
                        report['task_id'],
                        report['last_report']['@id'],
                        report['last_report']['scan_end'],
                        report['last_report']['timestamp'],
                        report['last_report']['scan_start'],
                        report['last_report']['result_count']['false_positive'],
                        report['last_report']['result_count']['debug'],
                        report['last_report']['result_count']['hole'],
                        report['last_report']['result_count']['warning'],
                        report['last_report']['result_count']['info'],
                        report['last_report']['result_count']['log'],
                        report['last_report']['severity']
                    ]) + "\n"
                )


print_datetime('End  ')
