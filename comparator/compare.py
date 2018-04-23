import difflib
import filecmp
import json
import os



def are_dir_trees_equal(dir1, dir2):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names and contents are equal.

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and 
        there were no errors while accessing the directories or files, 
        False otherwise.
   """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
        len(dirs_cmp.funny_files)>0:
        dirs_cmp.report()
        return False
    (_, mismatch, errors) =  filecmp.cmpfiles(
        dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch)>0 or len(errors)>0:
        dirs_cmp.report()
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dir_trees_equal(new_dir1, new_dir2):
            dirs_cmp.report()
            return False
    return True

class Compare:
    """Class to compare 2 directories, saying what they have in common and what they have different """
    
    def __init__(self, dir_1, dir_2):
        """Constructor of the class"""
        self.path_dir_1 = dir_1
        self.path_dir_2 = dir_2
        
    def cmp_files_to_json(self, path, in_dir_1, in_dir_2, size, equal, diff):
        """function that create a json with the report of compare the file in 'path' inside the both directories """
        file_json = {   
                        "path:" : path, 
                        "in_dir_1" : in_dir_1,
                        "in_dir_2" : in_dir_2,
                        "size" : size,
                        "equal" : equal,
                        "diff" : diff
                    }  
        return json.dumps(file_json)
    def cmp_init(self):
        """Function that init a new comparision"""
        self.cmp_directories(self.path_dir_1, self.path_dir_2)
        
    def equal_files_to_json(self, equal_files,path_dir_1,path_dir_2):
        """functions that return a list of json, which contains """
        equal_files_json = []
        for fl in equal_files:
            file_path = os.path.join(path_dir_1, fl)
            file_size = os.path.getsize(file_path)
            equal_files_json.append(self.cmp_files_to_json(file_path, True, True, file_size, True, None))
        return equal_files_json

    def diff_files_to_json(self, diff_files,path_dir_1,path_dir_2):
        """functions that return a list of json, which contains """
        diff_files_json = []
        for fl in diff_files:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_path_2 = os.path.join(path_dir_2, fl)
            file_size = os.path.getsize(file_path_1)
            
            with open(file_path_1) as file_1:
                with open(file_path_2) as file_2:
                    d = difflib.Differ()
                    diff = list(d.compare(file_1.readlines(), file_2.readlines()))
                    with open('diff.txt', 'w') as diff_file:
                        _diff = ''.join(diff)
                        diff_file.write(_diff)

                        ## access by indice :(

            #diff_report = os.popen('diff ' + file_path_1 + ' ' + file_path_2 ).read()
            #print '------------------------->' + diff_report
            #diff_files_json.append(self.cmp_files_to_json(file_path_1, True, True, file_size, True, diff_report))
        return diff_files_json

    def cmp_files(self,file_1='./',file_2='./'):
        """function that receive 2 path of files and return the report of compare both"""

        return json.dumps(self.cmp_files_to_json('hi', './', './', 1024, 'yes', None))

    def cmp_directories(self, dir_1='./',dir_2='./' ):
        """function that receive 2 path of directories and return the report of compare both in a json"""
        dirs_cmp = filecmp.dircmp(dir_1, dir_2)
        equal_files = dirs_cmp.same_files
        diff_files = dirs_cmp.diff_files  
        common_dir = dirs_cmp.common_dirs

        equal_files_json = self.equal_files_to_json(equal_files, dir_1, dir_2)
        diff_files_json = self.diff_files_to_json(diff_files, dir_1, dir_2)
        print equal_files_json 
        print diff_files_json
        for common_dir in dirs_cmp.common_dirs:
            new_dir_1 = os.path.join(dir_1, common_dir)
            new_dir_2 = os.path.join(dir_2, common_dir)

if __name__== "__main__":
    compare = Compare("../../inst/usr/local/rti_connext_dds-5.3.0/include/ndds", '../../rti_connext_dds-5.3.0/include/ndds')
  
     #print (compare.cmp_files(compare.path_dir_1,compare.path_dir_2)  )
    compare.cmp_init()