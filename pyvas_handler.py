from pyvas import Client


def get_report_from_task(tasks, processed_reports):
    reports_and_tasks = []
    for task in tasks:
        try:
            report_and_task = {
                'task_id': task['@id'],
                'task_name': task['name'],
                'last_report': task['last_report']['report']
            }
            if {
                'task_id': report_and_task['task_id'],
                'report_id': report_and_task['last_report']['@id']
            } not in processed_reports:
                reports_and_tasks.append(report_and_task)
        except KeyError:
            print("Skipping Task: " + task['@id'])
    return reports_and_tasks


def get_last_reports(instance, processed_reports):
    with Client(
            instance['host'],
            username=instance['username'],
            password=instance['password'],
            port=instance['port']
    ) as cli:
        return get_report_from_task(cli.list_tasks().data, processed_reports)


def download_report_as_csv(report_id, instance):
    with Client(
            instance['host'],
            username=instance['username'],
            password=instance['password'],
            port=instance['port']
    ) as cli:
        return cli.download_report(
            report_id,
            format_uuid=instance['format_uuid']
        )
