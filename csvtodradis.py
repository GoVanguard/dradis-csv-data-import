from json import dumps
from requests import Session
import csv
from sys import argv
from sys import exit
from argparse import ArgumentParser


class CsvToDradis(object):
    def __init__(self):
        self.arg = self.parse_args()
        if len(argv) != 6:
            print("wrong argument amount. see HELP")
            exit(-6)
        self._headers = {}
        self.title_column = 0      # 'title' column  in csv required for all exports
        self.node_name_column = 0  # 'node_name' column in csv required for both nodes exports
        self.issue_id_column = 0   # 'issue_id' column in csv required for nodes w/evidence exports
        # Dradis API Configuration
        self.dradis_api_token = self.arg.dradis_api_token
        self.dradis_project_id = self.arg.dradis_project_id
        self.dradis_url = self.arg.dradis_url
        self.dradis_issues_url = '{0}/pro/api/issues/'.format(self.dradis_url)
        self.dradis_nodes_url = '{0}/pro/api/nodes/'.format(self.dradis_url)
        self.session = Session()
        self.session.headers.update({'Authorization': 'Token token="{0}"'.format(self.dradis_api_token)})
        self.session.headers.update({'Dradis-Project-Id': self.dradis_project_id})
        self.session.headers.update({'Content-type': 'application/json'})

    def run(self):
        try:
            with open(self.arg.CSV_Filename)as csvfile:
                mycsv = csv.reader(csvfile, delimiter=',')
                headers = mycsv.__next__()
                self.csv_header_check(headers)
                if self.arg.issue:
                    self.create_issues(mycsv)
                elif self.arg.nodenote:
                    self.create_nodes_notes(mycsv)
                else:
                    self.create_nodes_evidence(mycsv)
        except Exception as e:
            print(e)
            exit(-1)
        self.session.close()
        print("Finished exporting.")
        return 0

    def create_issues(self, _csv):
        counter = 1
        for row in _csv:
            text = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
            for k in self._headers.keys():
                text += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
            issue_data = {'issue': {'text': text}}
            dradis = self.session.post(self.dradis_issues_url, data=dumps(issue_data), verify=False)
            if dradis.status_code == 201:
                print("Row {0} Issue was exported into Dradis". format(counter))
            else:
                print("Row {0} Issue was not exported into Dradis: {1}\n\n".format(counter, dradis.text))
            counter += 1
        return

    def create_nodes_notes(self, _csv):
        counter = 1
        for row in _csv:
            get_nodes = self.session.get(self.dradis_nodes_url)
            for n in get_nodes.json():
                if row[self.node_name_column].lower() == n['label'].lower():
                    notes = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                    for k in self._headers.keys():
                        notes += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    note = self.session.post(self.dradis_nodes_url + '{0}/notes'.format(n['id']),
                                             data=dumps({"note": {"text": notes}, "category_id": 1}))
                    if note.status_code == 201:
                        print("Row {0} Note was exported into Dradis\n\n".format(counter))
                    else:
                        print("Row {0} Note was not exported into Dradis: {1}\n\n".format(counter, note.text))
                    counter += 1
                    break
            else:
                notes = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                for k in self._headers.keys():
                    notes += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                node_data = {'node': {'label': row[self.node_name_column], "parent_id": None, 'type_id': 0}}
                node = self.session.post(self.dradis_nodes_url, data=dumps(node_data), verify=False)
                if node.status_code == 201:
                    print("Row {0} Node was exported into Dradis".format(counter))
                else:
                    print("Row {0} Node was not exported into Dradis: {1}".format(counter, node.text))
                note = self.session.post(self.dradis_nodes_url + '{0}/notes'.format(node.json()['id']),
                                         data=dumps({"note": {"text": notes}, "category_id": 1}))
                if note.status_code == 201:
                    print("Row {0} Note was exported into Dradis\n\n".format(counter))
                else:
                    print("Row {0} Note was not exported into Dradis: {1}\n\n".format(counter, note.text))
                counter += 1
        return

    def create_nodes_evidence(self, _csv):
        counter = 1
        for row in _csv:
            get_nodes = self.session.get(self.dradis_nodes_url)
            for n in get_nodes.json():
                if row[self.node_name_column].lower() == n['label'].lower():
                    content = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                    for k in self._headers.keys():
                        content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    evidence = self.session.post(self.dradis_nodes_url + '{0}/evidence'.format(n['id']),
                                                 data=dumps({"evidence": {"content": content,
                                                             "issue_id": row[self.issue_id_column]}}))
                    if evidence.status_code == 201:
                        print("Row {0} Evidence was exported into Dradis\n\n".format(counter))
                    else:
                        print("Row {0} Evidence was not exported into Dradis: {1}\n\n".format(counter, evidence.text))
                    counter += 1
                    break
            else:
                content = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                for k in self._headers.keys():
                    content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                node_data = {'node': {'label': row[self.node_name_column], "parent_id": None, 'type_id': 0}}
                node = self.session.post(self.dradis_nodes_url, data=dumps(node_data), verify=False)
                if node.status_code == 201:
                    print("Row {0} Node was exported into Dradis".format(counter))
                else:
                    print("Row {0} Node was not exported into Dradis: {1}".format(counter, node.text))
                evidence = self.session.post(self.dradis_nodes_url + '{0}/evidence'.format(node.json()['id']),
                                             data=dumps({"evidence": {"content": content,
                                                                      "issue_id": row[self.issue_id_column]}}))
                if evidence.status_code == 201:
                    print("Row {0} Evidence was exported into Dradis\n\n".format(counter))
                else:
                    print("Row {0} Evidence was not exported into Dradis: {1}\n\n".format(counter, evidence.text))
                counter += 1
        return

    def csv_header_check(self, headers):
        if "title" not in [h.lower() for h in headers]:
            print("The first row of your csv must have a column named 'title' that contains the titles of your "
                  "notes. Fix your csv and then try again.")
            exit(-1)
        if self.arg.nodenote:
            if "node_name" not in [h.lower() for h in headers]:
                print("For 'node w/note export' the first row of your csv must have a column named 'node_name'. "
                      "Fix your csv and try again.")
                exit(-1)
        elif self.arg.nodeevidence:
            if "node_name" not in [h.lower() for h in headers]:
                print("For 'node w/evidence export' the first row of your csv must have a column named "
                      "'node_name'. Fix your csv and try again.")
                exit(-1)
            elif "issue_id" not in [h.lower() for h in headers]:
                print("For 'node w/evidence export', the first row of your csv must have a column named "
                      "'issue_id' that contains the ids of the issues that you will use as evidence. "
                      "Fix your csv and try again.")
                exit(-1)
        counter = 0
        for header in headers:
            if self.arg.issue:
                if header.lower() == "title":
                    self.title_column = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1
            elif self.arg.nodenote:
                if header.lower() == "title":
                    self.title_column = counter
                    counter += 1
                elif header.lower() == "node_name":
                    self.node_name_column = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1
            else:
                if header.lower() == "title":
                    self.title_column = counter
                    counter += 1
                elif header.lower() == "node_name":
                    self.node_name_column = counter
                    counter += 1
                elif header.lower() == "issue_id":
                    self.issue_id_column = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1

    @staticmethod
    def parse_args():
        # parse the arguments
        parser = ArgumentParser(epilog='\tExample: \r\npython ' + argv[0] +
                                       " -i issues.csv https://dradis-pro.dev 21 xa632ghas87d393287",
                                description="Open .CSV  and export the data to Dradis as issues, nodes w/notes, or "
                                            "nodes w/evidence. 'title' heading required for all export types. "
                                            "'node_name' heading required for nodes w/evidence "
                                            "export & nodes w/note export. nodes w/evidence requires an 'issue_id' "
                                            "heading in your csv. If the node already exist then the remaining data "
                                            "will be added as a note or evidence depending on the export type\n Example"
                                            " issues export CSV heading layout: title,heading1,heading2,etc..\n\n"
                                            "Example nodes w/notes CSV heading layout: node_name,title,heading1,"
                                            "heading2,..etc\n\nExample nodes w/evidence CSV heading layout: "
                                            "node_name,title,issue_id,heading1,heading2,..etc\n\n")
        parser.add_argument('CSV_Filename', help=".csv filename")
        parser.add_argument('dradis_url', help="Dradis URL")
        parser.add_argument('dradis_project_id', help="Dradis Project ID")
        parser.add_argument('dradis_api_token', help="Dradis API token")
        parser.add_argument('-i', '--issue', action='store_true', help="store csv data in issues")
        parser.add_argument('-n', '--nodenote', action='store_true', help="store data in nodes and notes")
        parser.add_argument('-e', '--nodeevidence', action='store_true', help="store data in nodes and evidence."
                                                                              " make sure your csv has an issue_id "
                                                                              "column")
        return parser.parse_args()

if __name__ == "__main__":
    c = CsvToDradis()
    c.run()
