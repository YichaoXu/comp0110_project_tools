class CommitRecorder:
    
    class SourceRecorder:
        
        def __init__(self):
            self.__create_with = []  # String
            self.__delete_with = []  # String

        def record_create_with(self, test: str):
            self.__create_with.append(test)

        def record_delete_with(self, test: str):
            self.__delete_with.append(test)

    def __init__(self):
        self.__changes_map = {}  # String => SourceRecorder
        self.__added_test_in_the_commit = []  # String
        self.__removed_test_in_the_commit = []  # String
        self.__added_source_in_the_commit = []  # String
        self.__removed_source_in_the_commit = []  # String

    def add_test(self, name:str):
        self.__added_test_in_the_commit.append(name)

    def remove_test(self, name:str):
        self.__removed_test_in_the_commit.append(name)

    def add_source(self, name:str):
        self.__added_source_in_the_commit.append(name)

    def remove_source(self, name:str):
        self.__removed_source_in_the_commit.append(name)

    def change_name(self, old_name: str, new_name: str):
        if old_name not in self.__changes_map: return
        changed = self.__changes_map.pop(old_name)
        self.__changes_map[new_name] = changed

    def next_commit(self):
        for added_source in self.__added_source_in_the_commit:
            print(f'Source:{added_source}')
            if added_source not in self.__changes_map:
                self.__changes_map[added_source] = CommitRecorder.SourceRecorder()
            source_recorder = self.__changes_map[added_source]
            for added_test in self.__added_test_in_the_commit:
                print(f'\tCreate with: {added_test}')
                source_recorder.record_create_with(added_test)

        self.__added_test_in_the_commit = []
        self.__added_source_in_the_commit = []

        for removed_source in self.__removed_source_in_the_commit:
            print(f'Source:{removed_source}')
            if removed_source not in self.__changes_map:
                self.__changes_map[removed_source] = CommitRecorder.SourceRecorder()
            source_recorder = self.__changes_map[removed_source]
            for removed_test in self.__removed_test_in_the_commit:
                print(f'\tRemove with: {removed_test}')
                source_recorder.record_delete_with(removed_test)

        self.__removed_test_in_the_commit = []
        self.__removed_source_in_the_commit = []