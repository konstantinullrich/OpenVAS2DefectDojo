from xml.dom import minidom


def _xml_report_to_dict(xml_report):
    report = {
        "id": xml_report.attributes["id"].value
    }
    items = xml_report.childNodes
    for item in items:
        if item.nodeName != "#text" and item.nodeName != "result_count":
            if item.childNodes[0].nodeName == "#text":
                report[item.nodeName] = item.childNodes[0].nodeValue
    return report


def xml_to_dictionary(path):
    report_collection = []
    data = minidom.parse(path)
    items = data.documentElement.childNodes
    for item in items:
        if item.nodeName == "task":
            for item_child in item.childNodes:
                if item_child.nodeName == "first_report":
                    for report in item_child.childNodes:
                        if report.nodeName == "report":
                            report_collection.append(_xml_report_to_dict(report))
    return report_collection


def parse_openvas_task(path):
    report_collection = xml_to_dictionary(path)
    csv = "timestamp, id, severity"
    for report in report_collection:
        csv += "\n" + report["timestamp"] + ", " + report["id"] + ", " + report["severity"]
    print(csv)


parse_openvas_task("../demo_files/tasks_output.xml")
