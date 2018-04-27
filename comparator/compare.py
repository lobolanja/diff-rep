import difflib
import filecmp
import json
import os
from jinja2 import Template

NL='\n'

class Compare_to_md:
    """Class that receive a compare report and convert it to a MarkDown format"""
    def __init__(self, dir_1, dir_2, inform, file_="report.md"):
        self.h1 = Template('# {{title}}')
        self.h2 = Template('''
## {{text}}''')
        self.table_head = Template(
            '''
{% for key in dict_.keys() -%}
{{key}} | {% endfor %}''')
        self.table_line = Template(
            '''
{% for key in dict_.keys() -%}
--- | {% endfor %}''')
        self.table_row = Template(
            '''
{% for value in dict_.values() -%}
{{value}} | {% endfor %}''')
            
        self.h2_ = Template(
            '''{% for path in dict_.keys() %}

## {{path}}
                {% endfor %}
            ''')
        self.path_dir_1 = dir_1
        self.path_dir_2 = dir_2
        self.inform = inform 

        md = self.create_md(file_)
        self.write_report(md)

    def write_report(self, md,):
        md.write(self.h1.render(title="REPORT OF COMPARE "+ self.path_dir_1 + " AND " + self.path_dir_2 + NL ))
        for path in self.inform.keys() :
            md.write(self.h2.render(text = path + NL))
            md.write(self.table_head.render(dict_= self.inform[path]['files'][0]))
            md.write(self.table_line.render(dict_= self.inform[path]['files'][0]))
            for kk in self.inform[path]['files']:
                md.write(self.table_row.render(dict_= kk))
                str(kk) + NL

    def create_md(self, file_):
        return open(file_, 'w')

class Compare:
    """Class to compare 2 directories, saying what they have in common and what they have different """
    
    def __init__(self, dir_1, dir_2):
        """Constructor of the class"""
        self.path_dir_1 = dir_1
        self.path_dir_2 = dir_2

        #TO-DO possibly it is more correct to use an enum
        self.dir = "directory"
        self.file = "file"
        self.link = "link"
        

    def cmp_init(self):
        """Function that init a new comparision"""
        caca = json.loads(json.dumps(self.cmp_directories(self.path_dir_1, self.path_dir_2),sort_keys=True))
        self.report=Compare_to_md(self.path_dir_1, self.path_dir_2, caca)
        #print json.dumps(caca,sort_keys=True)
        #print self.cmp_directories(self.path_dir_1, self.path_dir_2)
        #self.cmp_directories(self.path_dir_1, self.path_dir_2)

    def get_type(self, path):

        #TO-DO try
        if os.path.isfile(path):
            return self.file
        elif os.path.isdir(path):
            return self.dir
        else:
            return self.link

    def are_dir_trees_equal(self, dir_1, dir_2):
        """
        Compare two directories recursively. Files in each directory are
        assumed to be equal if their names and contents are equal.

        @param dir1: First directory path
        @param dir2: Second directory path

        @return: True if the directory trees are the same and 
            there were no errors while accessing the directories or files, 
            False otherwise.
        """

        dirs_cmp = filecmp.dircmp(dir_1, dir_2)
        if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
            len(dirs_cmp.funny_files)>0:
            return False
        (_, mismatch, errors) =  filecmp.cmpfiles(dir_1, dir_2, dirs_cmp.common_files, shallow=False)
        if len(mismatch)>0 or len(errors)>0:
            return False
        for common_dir in dirs_cmp.common_dirs:
            new_dir_1 = os.path.join(dir_1, common_dir)
            new_dir_2 = os.path.join(dir_2, common_dir)
            if not self.are_dir_trees_equal(new_dir_1, new_dir_2):
                return False
        return True

    def directory_to_json(self, path, list_in ):
        """Function that create a json with the report of compare the content of both directories """
        directory_json={"base_path": path ,"files": list_in }
        #print "base_path : " + path
        return directory_json

    def cmp_files_to_json(self, path, type_, in_dir_1, in_dir_2, size_1, size_2, equal, diff):
        """Function that create a json with the report of compare the file in 'path' inside the both directories """

        file_json = {   
                        "aname" : path, #path of the file/directory after the base path
                        "type" : type_, # file, directory or link
                        "in_dir_1" : in_dir_1,
                        "in_dir_2" : in_dir_2,
                        "size_1" : size_1,
                        "size_2" : size_2,
                        "equal" : equal,
                        #"diff" : diff
                    }  
        return json.loads(json.dumps(file_json, sort_keys=True))
        
    def equal_files_to_json(self, equal_files, path_dir_1, path_dir_2):
        """Functions that return a list of json, which contains equal files report"""
        equal_files_json = []
        for fl in equal_files:
            file_path = os.path.join(path_dir_1, fl)
            file_size_1 = os.path.getsize(file_path)
            file_size_2 = os.path.getsize(os.path.join(path_dir_2, fl))
            equal_files_json.append(self.cmp_files_to_json(file_path, self.get_type(file_path), True, True, file_size_1, file_size_2, True, None))
        return equal_files_json

    def diff_files_to_json(self, diff_files, path_dir_1, path_dir_2):
        """Functions that return a list of json, which contains diff files report """
        diff_files_json = []
        for fl in diff_files:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_path_2 = os.path.join(path_dir_2, fl)
            file_size_1 = os.path.getsize(file_path_1)
            file_size_2 = os.path.getsize(os.path.join(path_dir_2, fl))
            
            diff_report = self.make_diff(file_path_1, file_path_2)
            diff_files_json.append(self.cmp_files_to_json(file_path_1, self.get_type(file_path_1), True, True, file_size_1, file_size_2, False, diff_report))

        return diff_files_json

    def make_diff(self, file_path_1, file_path_2):
        """Function that receive 2 path of files and return the diff report of compare both"""
        with open(file_path_1) as file_1:
            with open(file_path_2) as file_2:
                d = difflib.Differ()

                diff = list(d.compare(file_1.readlines(), file_2.readlines()))
                _diff = []

                for i in range(len(diff)-1):
                    if(diff[i][0] == '+' or diff[i][0] == '-'):
                        _diff.append(diff[i])

                return ''.join(_diff)

    def only_in_one_to_json(self, path_dir_1, list_in_1, path_dir_2, list_in_2):
        """Functions that receive 2 path and 2 list of the files and directories that are only in the first path and in the second path respectively""" 
        only_in_one_json = []
        for fl in list_in_1:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_size_1 = os.path.getsize(file_path_1)
            type_ = self.get_type(file_path_1)
            if (type_ == self.dir):
                file_size_1 = None
            only_in_one_json.append(self.cmp_files_to_json(file_path_1, type_ , True, False, file_size_1, None, False, None))

        for fl in list_in_2:
            file_path_2 = os.path.join(path_dir_2, fl)
            file_size_2 = os.path.getsize(file_path_2)
            type_ = self.get_type(file_path_2)
            if (type_ == self.dir):
                file_size_2 = None
            
            only_in_one_json.append(self.cmp_files_to_json(file_path_2, type_ , False, True, None, file_size_2, False, None))

        return  only_in_one_json

    def common_dirs_to_json(self, list_common_dirs, path_dir_1, path_dir_2):
        """Functions that return a list of json, which contains diff files report """
        common_dirs_json = []
        
        for directory in list_common_dirs:
            file_path_1 = os.path.join(path_dir_1, directory)
            file_path_2 = os.path.join(path_dir_2, directory)

            common_dirs_json.append(
                                    self.cmp_files_to_json(
                                                            file_path_1,
                                                            self.get_type(file_path_1),
                                                            True,
                                                            True,
                                                            None, #size dir 1
                                                            None, #size dir 2 
                                                            self.are_dir_trees_equal(file_path_1, file_path_2),
                                                            None #TO-DO
                                                            )
                                    )
        return common_dirs_json

    def internal_directories_json(self,path_dir_1, path_dir_2, common_dirs):
        """"""
        list_dirs_json = {}

        for dir_ in common_dirs:
            dir_path_1 = os.path.join(path_dir_1, dir_)
            dir_path_2 = os.path.join(path_dir_2, dir_)
            list_dirs_json.update(self.cmp_directories(dir_path_1, dir_path_2))

        return list_dirs_json

    def cmp_directories(self, dir_1='./',dir_2='./' ):
        """Function that receive 2 path of directories and return the report of compare both in a json"""
        dirs_cmp = filecmp.dircmp(dir_1, dir_2)
        list_dirs_json = dict()

        equal_files_json = self.equal_files_to_json(dirs_cmp.same_files, dir_1, dir_2)
        diff_files_json  = self.diff_files_to_json(dirs_cmp.diff_files, dir_1, dir_2)
        only_in_one_json = self.only_in_one_to_json(dir_1, dirs_cmp.left_only, dir_2, dirs_cmp.right_only)
        common_dirs_json = self.common_dirs_to_json(dirs_cmp.common_dirs, dir_1, dir_2)

        all_lists_json = json.loads(json.dumps(list(equal_files_json + diff_files_json + only_in_one_json + common_dirs_json),sort_keys=True))
        #print self.directory_to_json(dir_1,list(equal_files_json + diff_files_json + only_in_one_json))
        #list_dirs_json.append(self.directory_to_json(dir_1, all_lists_json))
        if dirs_cmp.common_dirs: 
            list_dirs_json = self.internal_directories_json(dir_1, dir_2, dirs_cmp.common_dirs)
        list_dirs_json.update(dict({dir_1 : self.directory_to_json(dir_1,all_lists_json)}))

        return list_dirs_json
  
        
        
        

if __name__== "__main__":
    compare = Compare("/home/juanca/task/inst/usr/local/rti_connext_dds-5.3.0/include/ndds", '/home/juanca/task/rti_connext_dds-5.3.0/include/ndds')
  
     #print (compare.cmp_files(compare.path_dir_1,compare.path_dir_2)  )
    compare.cmp_init()