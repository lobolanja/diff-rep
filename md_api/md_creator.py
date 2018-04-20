import json
data = {"tables":[{"directory":"a","rows":[{"path":"route","type":"file","match":"yes","issue":"null"},{"path":"route2","type":"directory","match":"warn","issue":"null"}]},{"directory":"b","rows":[{"path":"route2","type":"directory","match":"warn","issue":"null"}]}]}

data_string=json.dumps(data)
#print  data_string
def make_row(path="./", type="file",match="warning",issue=None):
    return {"path" : path, "type":type, "match":match, "issue":issue}

#print make_row()

data["tables"][0]["rows"].append(make_row())
print data_string