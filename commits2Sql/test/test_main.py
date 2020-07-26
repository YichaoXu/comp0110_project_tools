import os
from pydriller import RepositoryMining


path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'
path_to_repository = f'{path_to_comp0110}/example_repositories/pydriller_test'

repos = RepositoryMining(path_to_repository)
count = 0
for commit in repos.traverse_commits():
    count += 1
    for file in commit.modifications:
        after_set = set(file.methods)
        before_set = set(file.methods_before)
        changed_set = set(file.changed_methods)
        name_unchanged = before_set & after_set
        removed_and_renamed_bf = before_set - name_unchanged
        created_and_renamed_af = after_set - name_unchanged
        modified = changed_set - (removed_and_renamed_bf | created_and_renamed_af)

