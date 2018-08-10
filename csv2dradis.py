import pydradis3
from json import dumps
import csv
from sys import argv, exit, version
from argparse import ArgumentParser

class CsvToDradis(object):
    def __init__(self):
        self.arg = self.processArguments()
        if len(argv) != 6:
            print("wrong argument amount. see HELP")
            exit(-6)
        # Parsing Defaults
        self.titleColumn = 0      # 'title' column  in csv required for all exports
        self.nodeNameColumn = 0  # 'node_name' column in csv required for both nodes exports
        self.issueIdColumn = 0   # 'issue_id' column in csv required for nodes w/evidence exports
        # Dradis API Configuration
        self.verifyCert = True    # change this to make requests without verifying
        self.dradisApiToken = self.arg.dradisApiToken
        self.dradisProjectId = self.arg.dradisProjectId
        self.dradisUrl = self.arg.dradisUrl
        self.dradisDebug = False
        self.dradisSession = Pydradis3(self.dradisApiToken, self.dradisUrl, self.dradisDebug, self.verifyCert)

    def run(self):
        try:
            with open(self.arg.csvFilename)as csvfile:
                csvObj = csv.reader(csvfile, delimiter=',')
                # Python 2.x and 3.x compatibility
                if version > '3':
                    headers = csvObj.__next__()
                else:
                    headers = csvObj.next()
                self.csvHeaderCheck(headers)
                if self.arg.issue:
                    self.createIssues(csvObj)
                elif self.arg.nodeNote:
                    self.createNodesNotes(csvObj)
                else:
                    self.createNodesEvidence(csvObj)
        except Exception as e:
            print(e)
            exit(-1)
        self.dradisSession = None
        print("Finished exporting.")
        return 0

    def createIssues(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            text = '#[Title]#\r\n' + row[self.titleColumn] + '\r\n\r\n'
            # Process each column into the dictionary payload
            for k in self._headers.keys():
                text += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
            data = {'issue': {'text': text}}
            # Call create_issue_raw from pydradis3 which accepts a manually constructed payload as data
            createIssue = self.dradisSession.create_issue_raw(self.dradisProjectId, data=data)
            if createIssue:
                print("Row {0} Issue was exported into Dradis".format(counter))
            else:
                print("Row {0} Issue was not exported into Dradis".format(counter))
        return

    def createNodesNotes(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            # Get a list of existing nodes from pydradis3
            get_nodes = self.dradisSession.get_nodelist(self.dradisProjectId)
            for n in get_nodes.json():
                # Create note on a matched node
                if row[self.nodeNameColumn].lower() == n['label'].lower():
                    notes = '#[Title]#\r\n' + row[self.titleColumn] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        notes += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    data = {"note": {"text": notes}, "category_id": 1}
                    # Call create_node_raw from pydradis3 which accepts a manually constructed payload as data
                    createNote = self.dradisSession.create_note_raw(self.dradisProjectId, node_id=n['id'], data=data)
                if createNote:
                    print("Row {0} Node was exported into Dradis".format(counter))
                else:
                    print("Row {0} Node was not exported into Dradis".format(counter))
        return

    def createNodesEvidence(self, csv):
        counter = 0
        for row in csv:
            counter = counter + 1
            # Get a list of existing nodes from pydradis
            get_nodes = self.dradisSession.get_nodelist(self.dradisProjectId)
            for n in get_nodes.json():
                # Create evidence on matched node
                if row[self.nodeNameColumn].lower() == n['label'].lower():
                    content = '#[Title]#\r\n' + row[self.titleColumn] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createEvidence = self.dradisSession.create_evidence_raw(pid=self.dradisProjectId, node_id=n['id'], issue_id=row[self.issueIdColumn], data=content)
                # Node does not exist, so create it then create evidence
                else:
                    content = '#[Title]#\r\n' + row[self.titleColumn] + '\r\n\r\n'
                    # Process each column into the dictionary payload
                    for k in self._headers.keys():
                        content += '#[{0}]#\r\n'.format(self._headers[k]) + '{0}\r\n'.format(row[int(k)]) + '\r\n\r\n'
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createNode = self.dradisSession.create_node(pid=self.dradisProjectId, label=row[self.nodeNameColumn], type_id=0, parent_id=None, position=1)
                    if createNode:
                        print("Row {0} Node was exported into Dradis".format(counter))
                    else:
                        print("Row {0} Node was not exported into Dradis".format(counter))
                        continue
                    # Call create_evidence_raw from pydradis3 which accepts a manually constructed content payload as data
                    createEvidence = self.dradisSession.create_evidence_raw(pid=self.dradisProjectId, node_id=row[self.nodeNameColumn], issue_id=row[self.issueIdColumn], data=content)
                if createEvidence:
                    print("Row {0} Evidence was exported into Dradis\n\n".format(counter))
                else:
                    print("Row {0} Evidence was not exported into Dradis\n\n".format(counter))
        return

    def csvHeaderCheck(self, headers):
        print(headers)
        if "title" not in [h.lower() for h in headers]:
            print("The first row of your csv must have a column named 'title' that contains the titles of your "
                  "notes. Fix your csv and then try again.")
            exit(-1)
        if self.arg.nodeNote:
            if "node_name" not in [h.lower() for h in headers]:
                print("For 'node w/note export' the first row of your csv must have a column named 'node_name'. "
                      "Fix your csv and try again.")
                exit(-1)
        elif self.arg.noEvidence:
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
                    self.titleColumn = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1
            elif self.arg.nodeNote:
                if header.lower() == "title":
                    self.titleColumn = counter
                    counter += 1
                elif header.lower() == "node_name":
                    self.nodeNameColumn = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1
            else:
                if header.lower() == "title":
                    self.titleColumn = counter
                    counter += 1
                elif header.lower() == "node_name":
                    self.nodeNameColumn = counter
                    counter += 1
                elif header.lower() == "issue_id":
                    self.issueIdColumn = counter
                    counter += 1
                else:
                    self._headers[str(counter)] = header
                    counter += 1

    @staticmethod
    def processArguments():
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
        parser.add_argument('csvFilename', help=".csv filename")
        parser.add_argument('dradisUrl', help="Dradis URL")
        parser.add_argument('dradisProjectId', help="Dradis Project ID")
        parser.add_argument('dradisApiToken', help="Dradis API token")
        parser.add_argument('-i', '--issue', action='store_true', help="store csv data in issues")
        parser.add_argument('-n', '--nodeNote', action='store_true', help="store data in nodes and notes")
        parser.add_argument('-e', '--noEvidence', action='store_true', help="store data in nodes and evidence."
                                                                              " make sure your csv has an issue_id "
                                                                              "column")
        return parser.parse_args()

if __name__ == "__main__":
    c = CsvToDradis()
    c.run()
