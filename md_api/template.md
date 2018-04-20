# Dir1

PATH | TYPE | MATCH | ISSUE
---|---|---|---
dir1/file1 | file | YES | NONE
dir1/file2 | file | YES | NONE
dir1/file3 | file | NO | DIFF
dir1/file4 | file | YES | NONE
[dir1/directory1](# Dir1/directory1 ) | directory | YES | NONE
[dir1/directory2](# Dir1/directory2) | directory | NO | file no match
[dir1/directory3] | directory | YES | NONE

# Dir1/directory1

PATH | TYPE | MATCH | ISSUE
---|---|---|---
dir1/file1 | file | YES | NONE
dir1/file2 | file | YES | NONE
dir1/file3 | file | NO | DIFF
dir1/file4 | file | YES | NONE
[dir1/directory1/dir] | directory | YES | NONE

# Dir1/directory2

PATH | TYPE | MATCH | ISSUE
---|---|---|---
dir1//directory2/file1 | file | YES | NONE
dir1//directory2/file2 | file | YES | NONE
dir1//directory2/file3 | file | NO | DIFF


