import argparse
import json
import subprocess

import pandas as pd
from pydriller import Repository
from datetime import datetime
import tempfile


def get_readability(source):
    with tempfile.NamedTemporaryFile(suffix='.java', delete=False) as java_file:
        java_file.write(str.encode(source))

        cmd_list = ["java", "-jar", "rsm.jar"] + [java_file.name]

        readability_str = subprocess.check_output(cmd_list, cwd="readability(1)").decode("utf-8")

    return float((readability_str.split("\n")[2]).split("\t")[1])


def main():
    to = datetime(2022, 12, 31, 0, 0, 0)
    parser = argparse.ArgumentParser(description='Process a repository URL.')
    parser.add_argument('--url', type=str, help='the URL of the repository')
    args = parser.parse_args()
    result = {}
    readability = []
    # Use PyDriller to iterate over the commits in the repository
    for commit in Repository(args.url, only_modifications_with_file_types=['.java'], only_in_branch='master',
                             to=to).traverse_commits():

        # Check if the commit was made before or on 2022-12-31
        if not commit.modified_files:
            continue
        for modified in commit.modified_files:
            if modified.source_code and modified.source_code_before and modified.filename.endswith(".java"):
                # Save Data in a list to get a csv output
                result = {
                        'commit_hash': commit.hash,
                        'commit_msg': commit.msg,
                        'committer_name': commit.committer.name,
                        'commiter_email': commit.committer.name,
                        'commit_data': str(commit.committer_date),
                        'author_name': commit.author.name,
                        'author_email': commit.author.email,
                        'total_changes': commit.lines,
                        'file_name': modified.filename,
                        'old_path': modified.old_path,
                        'new_path': modified.new_path,
                        'source_code_before': modified.source_code_before,
                        'source_code': modified.source_code,
                        'complexity': modified.complexity,
                        'nloc': modified.nloc,
                    }

                read1 = get_readability(modified.source_code)
                read2 = get_readability(modified.source_code_before)

                result['readability'] = read1 - read2
                # print("readability of current source code", read1)
                # print("readability of before source code", read2)
                # print("diffrence between after and before:", read2 - read1)
                # print("result readability:", result)

                with open(".json", "w") as outfile:
                    json.dump(result, outfile)
    df = pd.DataFrame(result, columns= ['commit_hash', 'commit_msg', 'committer_name', 'committer_email', 'commit_data',
                                        'author_name', 'author_email'
                                        'total_changes', 'file_name', 'old_path', 'new_path',
                                        'source_code_before', 'source_code', 'complexity', 'nloc', 'readability'])
    df.to_csv("result_commonvfs.csv", index=False)

if __name__ == '__main__':
    main()
