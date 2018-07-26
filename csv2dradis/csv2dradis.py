import pydradis3
from json import dumps
from requests import Session
import csv
from sys import argv, exit, version
from argparse import ArgumentParser


class CsvToDradis(object):
    def __init__(self):
        self.arg = self.parse_args()
        if len(argv) != 6:
            print("wrong argument amount. see HELP")
            exit(-6)
        # Parsing Defaults
        self.title_column = 0      # 'title' column  in csv required for all exports
        self.node_name_column = 0  # 'node_name' column in csv required for both nodes exports
        self.issue_id_column = 0   # 'issue_id' column in csv required for nodes w/evidence exports
        # Dradis API Configuration
        self.verify_cert = True    # change this to make requests without verifying
        self.dradis_api_token = self.arg.dradis_api_token
        self.dradis_project_id = self.arg.dradis_project_id
        self.dradis_url = self.arg.dradis_url
        self.dradis_debug = False
        self.dradis_session = Pydradis3(self.dradis_api_token, self.dradis_url, self.dradis_debug, self.verify_cert)

    def run(self):
        try:
            with open(self.arg.CSV_Filename)as csvfile:
                csvObj = csv.reader(csvfile, delimiter=',')
                # Python 2.x and 3.x compatibility
                if version > '3':
                    headers = csvObj.__next__()
                else:
                    headers = csvObj.next()
                self.csv_header_check(headers)
                if self.arg.issue:
                    self.create_issues(csvObj)
                elif self.arg.nodenote:
                    self.create_nodes_notes(csvObj)
                else:
                    self.create_nodes_evidence(csvObj)
        except Exception as e:
            print(e)
            exit(-1)
        self.dradis_session = None
        print("Finished exporting.")
        return 0

    def create_issues(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            text = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
            # Process each column into the dictionary payload
            for k in self._headers.keys():
                text += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
            data = {'issue': {'text': text}}
            # Call create_issue_raw from pydradis3 which accepts a manually constructed payload as data
            createIssue = self.dradis_session.create_issue_raw(self.dradis_project_id, data=data)
            if createIssue:
                print("Row {0} Issue was exported into Dradis".format(counter))
            else:
                print("Row {0} Issue was not exported into Dradis".format(counter))
        return

    def create_nodes_notes(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            # Get a list of existing nodes from pydradis3
            get_nodes = self.dradis_session.get_nodelist(self.dradis_project_id)
            for n in get_nodes.json():
                # Create note on a matched node
                if row[self.node_name_column].lower() == n['label'].lower():
                    notes = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        notes += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    data = {"note": {"text": notes}, "category_id": 1}
                    # Call create_node_raw from pydradis3 which accepts a manually constructed payload as data
                    createNote = self.dradis_session.create_note_raw(self.dradis_project_id, node_id=n['id'], data=data)
                if createNote:
                    print("Row {0} Node was exported into Dradis".format(counter))
                else:
                    print("Row {0} Node was not exported into Dradis".format(counter))
        return

    def create_nodes_evidence(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            # Get a list of existing nodes from pydradis
            get_nodes = self.dradis_session.get_nodelist(self.dradis_project_id)
            for n in get_nodes.json():
                # Create evidence on matched node
                if row[self.node_name_column].lower() == n['label'].lower():
                    content = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createEvidence = self.dradis_session.create_evidence_raw(pid=self.dradis_project_id, node_id=n['id'], issue_id=row[self.issue_id_column], data=content)
                # Node does not exist, so create it then create evidence
                else:
                    content = '#[Title]#\r\n' + row[self.title_column] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createNode = self.dradis_session.create_node(pid=self.dradis_project_id, label=row[self.node_name_column], type_id=0, parent_id=None, position=1)
                    if createNode:
                        print("Row {0} Node was exported into Dradis".format(counter))
                    else:
                        print("Row {0} Node was not exported into Dradis".format(counter))
                        continue
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createEvidence = self.dradis_session.create_evidence_raw(pid=self.dradis_project_id, node_id=row[self.node_name_column], issue_id=row[self.issue_id_column], data=content)
                if createEvidence:
                    print("Row {0} Evidence was exported into Dradis\n\n".format(counter))
                else:
                    print("Row {0} Evidence was not exported into Dradis\n\n".format(counter))
        return

    def csv_header_check(self, headers):
        print(headers)
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
