from pydriller import RepositoryMining

path_to_repository = '../../example_repositories/pydriller-test'

project_repository = RepositoryMining(path_to_repository)
for commit in project_repository.traverse_commits():
    commit.modifications
