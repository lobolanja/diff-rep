"""Todo."""
import difflib
import filecmp
import json
import markdown
from jinja2 import Environment, PackageLoader
import os
import sys


class compareHeaders:
    """
    Class to compare 2 directories, saying what they have in common and
    what they have different
    """

    def __init__(self, dir_1, dir_2):
        """Todo."""
        self.path_dir_1 = dir_1
        self.path_dir_2 = dir_2
        self.inform = dict()

        # types of files        #
        self.dir = "directory"  #
        self.file = "file"      #
        self.link = "link"      #

    def write_report_md(self):
        """Todo."""
        md = open('report.md', 'w')

        env = Environment(loader=PackageLoader('compare', 'templates'))
        template = env.get_template('md_template.jn2')

        md.write(template.render(
                                    path_1=self.path_dir_1,
                                    path_2=self.path_dir_2,
                                    inform=self.inform))

        html = open('report.html', 'w')
        html.write(
            markdown.markdown(
                template.render(
                    path_1=self.path_dir_1,
                    path_2=self.path_dir_2,
                    inform=self.inform),
                extensions=['markdown.extensions.tables']
                )
                )

    def cmp_init(self):
        """Init a new comparision."""
        self.inform = json.loads(
                        json.dumps(
                            self.cmp_directories(
                                self.path_dir_1,
                                self.path_dir_2),
                            sort_keys=True))
        self.write_report_md()

    def get_type(self, path):
        """Todo."""
        if os.path.isfile(path):
            return self.file
        elif os.path.isdir(path):
            return self.dir
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
        if dirs_cmp.left_only or dirs_cmp.right_only or \
                dirs_cmp.funny_files:
            return False
        (_, mismatch, errors) = filecmp.cmpfiles(
                                            dir_1, dir_2,
                                            dirs_cmp.common_files,
                                            shallow=False)
        if mismatch or errors:
            return False
        for common_dir in dirs_cmp.common_dirs:
            new_dir_1 = os.path.join(dir_1, common_dir)
            new_dir_2 = os.path.join(dir_2, common_dir)
            if not self.are_dir_trees_equal(new_dir_1, new_dir_2):
                return False
        return True

    def directory_to_json(self, path, list_in):
        """
        Create a json with the report of compare the content
        of both directories.
        """
        directory_json = {"base_path": path, "files": list_in}
        return directory_json

    def cmp_files_to_json(
                            self,
                            path,
                            type_,
                            in_dir_1,
                            in_dir_2,
                            size_1,
                            size_2,
                            equal,
                            diff
                        ):
        """
        Create a json with the report of compare the file in
        'path' inside the both directories
        """

        file_json = {
                        "path": path,
                        "type": type_,
                        "in_dir_1": in_dir_1,
                        "in_dir_2": in_dir_2,
                        "size_1": size_1,
                        "size_2": size_2,
                        "equal": equal,
                        "diff": diff
                    }
        return json.loads(json.dumps(file_json, sort_keys=True))

    def equal_files_to_json(self, equal_files, path_dir_1, path_dir_2):
        """Return a list of json, which contains equal files report."""
        equal_files_json = []
        for fl in equal_files:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_path_2 = os.path.join(path_dir_2, fl)
            path_in = self.make_path_in(file_path_1, file_path_2)

            file_size_1 = os.path.getsize(file_path_1)
            file_size_2 = os.path.getsize(file_path_2)
            equal_files_json.append(
                            self.cmp_files_to_json(
                                                path_in,
                                                self.get_type(file_path_1),
                                                True,
                                                True,
                                                file_size_1,
                                                file_size_2,
                                                True,
                                                None)
                                    )
        return equal_files_json

    def diff_files_to_json(self, diff_files, path_dir_1, path_dir_2):
        """Return a list of json, which contains diff files report."""
        diff_files_json = []
        for fl in diff_files:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_path_2 = os.path.join(path_dir_2, fl)
            path_in = self.make_path_in(file_path_1, file_path_2)

            file_size_1 = os.path.getsize(file_path_1)
            file_size_2 = os.path.getsize(file_path_2)

            hash_ = self.make_diff(file_path_1, file_path_2, path_in)
            if hash_ is not None:
                diff_files_json.append(
                    self.cmp_files_to_json(
                        path_in,
                        self.get_type(file_path_1),
                        True,
                        True,
                        file_size_1,
                        file_size_2,
                        False,
                        '['+hash_+'](./diff/'+hash_+')'))
            else:
                diff_files_json.append(
                                        self.cmp_files_to_json(
                                                    path_in,
                                                    self.get_type(file_path_1),
                                                    True,
                                                    True,
                                                    file_size_1,
                                                    file_size_2,
                                                    True,
                                                    hash_
                                                    )
                                        )
        return diff_files_json

    def make_path_in(self, path_1, path_2):
        """Todo."""
        r_pos = -1
        path = ""
        while(path_2.find(path_1[r_pos:]) != -1):
            path = path_1[r_pos:]
            r_pos -= 1
        return path

    def make_diff(self, file_path_1, file_path_2, path_in):
        """Receive 2 path of files and return the diff report of compare
        both.
        """
        hash_ = hash(path_in)

        with open(file_path_1) as file_1:
            with open(file_path_2) as file_2:
                d = difflib.Differ()

                diff = list(d.compare(file_1.readlines(), file_2.readlines()))
                _diff = []

                for i in range(len(diff)-1):
                    if(diff[i][0] == '+' or diff[i][0] == '-'):
                        if(diff[i].find('Copyright') == -1 and
                                diff[i].find("generated by:") == -1):
                            _diff.append(diff[i])

                if _diff:
                    _diff = ''.join(_diff)
                    try:
                        f = open('./diff/' + str(hash_) + '.diff', 'w')
                    except:
                        os.mkdir('./diff')
                        f = open('./diff/' + str(hash_) + '.diff', 'w')
                    f.write(_diff)
                    f.close()
                    return str(hash_)+'.diff'
                return None

    def only_in_one_to_json(
                            self,
                            path_dir_1,
                            list_in_1,
                            path_dir_2,
                            list_in_2):
        """Receive 2 path and 2 list of the files and
        directories that are only in the first path and in the second
        path respectively
        """

        only_in_one_json = []
        for fl in list_in_1:
            file_path_1 = os.path.join(path_dir_1, fl)
            file_size_1 = os.path.getsize(file_path_1)
            type_ = self.get_type(file_path_1)
            if (type_ == self.dir):
                file_size_1 = None
            only_in_one_json.append(self.cmp_files_to_json(
                                                            file_path_1,
                                                            type_,
                                                            True,
                                                            False,
                                                            file_size_1,
                                                            None,
                                                            False,
                                                            None))

        for fl in list_in_2:
            file_path_2 = os.path.join(path_dir_2, fl)
            file_size_2 = os.path.getsize(file_path_2)
            type_ = self.get_type(file_path_2)
            if (type_ == self.dir):
                file_size_2 = None

            only_in_one_json.append(self.cmp_files_to_json(
                                                            file_path_2,
                                                            type_,
                                                            False,
                                                            True,
                                                            None,
                                                            file_size_2,
                                                            False,
                                                            None))

        return only_in_one_json

    def common_dirs_to_json(self, list_common_dirs, path_dir_1, path_dir_2):
        """Return a list of json, which contains diff files report."""
        common_dirs_json = []

        for directory in list_common_dirs:
            file_path_1 = os.path.join(path_dir_1, directory)
            file_path_2 = os.path.join(path_dir_2, directory)
            path_in = self.make_path_in(file_path_1, file_path_2)

            common_dirs_json.append(
                self.cmp_files_to_json(
                    path_in,
                    self.get_type(file_path_1),
                    True,
                    True,
                    None,
                    None,
                    self.are_dir_trees_equal(file_path_1, file_path_2),
                    None
                    )
                )
        return common_dirs_json

    def internal_directories_json(self, path_dir_1, path_dir_2, common_dirs):
        """Todo."""
        list_dirs_json = {}

        for dir_ in common_dirs:
            dir_path_1 = os.path.join(path_dir_1, dir_)
            dir_path_2 = os.path.join(path_dir_2, dir_)
            list_dirs_json.update(self.cmp_directories(dir_path_1, dir_path_2))

        return list_dirs_json

    def cmp_directories(self, dir_1='./', dir_2='./'):
        """
        Receive 2 path of directories and return the report of compare both
        in a json.
        """
        dirs_cmp = filecmp.dircmp(dir_1, dir_2)
        list_dirs_json = dict()
        path_in = self.make_path_in(dir_1, dir_2)

        equal_files_json = self.equal_files_to_json(
                                            dirs_cmp.same_files,
                                            dir_1,
                                            dir_2
                                            )

        diff_files_json = self.diff_files_to_json(
                                            dirs_cmp.diff_files,
                                            dir_1,
                                            dir_2
                                            )
        only_in_one_json = self.only_in_one_to_json(
                                            dir_1,
                                            dirs_cmp.left_only,
                                            dir_2,
                                            dirs_cmp.right_only
                                            )
        common_dirs_json = self.common_dirs_to_json(
                                            dirs_cmp.common_dirs,
                                            dir_1,
                                            dir_2
                                            )

        all_lists_json = json.loads(
                                json.dumps(
                                    list(
                                        equal_files_json +
                                        diff_files_json +
                                        only_in_one_json +
                                        common_dirs_json
                                        ),
                                    sort_keys=True))
        if dirs_cmp.common_dirs:
            list_dirs_json = self.internal_directories_json(
                                                        dir_1,
                                                        dir_2,
                                                        dirs_cmp.common_dirs
                                                        )
        list_dirs_json.update(
            dict({path_in: self.directory_to_json(path_in, all_lists_json)})
            )

        return list_dirs_json

if __name__ == "__main__":
    if len(sys.argv) == 3:
        compare = Compare(sys.argv[1], sys.argv[2])
        compare.cmp_init()
    else:
        try:
            compare = Compare(
                "../../inst/usr/local/rti_connext_dds-5.3.0/include",
                "../../rti_connext_dds-5.3.0/include"
                )
            compare.cmp_init()
        except:
            print('For use this script, you should give 2 argument, path of\
             the directories to compare')
