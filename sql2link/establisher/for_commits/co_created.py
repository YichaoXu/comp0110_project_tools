from establisher.abs_link_builder import AbsLinkEstablisher


class CoCreatedInCommitLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str:
        return '''
        DROP TABLE IF EXISTS co_created_for_commits
        '''

    @property
    def _initial_table_sql(self) -> str:
        return '''
        CREATE TABLE co_created_for_commits (
            tested_method_id INTEGER NOT NULL,
            test_method_id INTEGER NOT NULL,
            FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
            FOREIGN KEY (test_method_id) REFERENCES methods(id)
        );
        '''

    @property
    def _insert_new_row_sql(self) -> str:
        return '''
        INSERT INTO co_created_for_commits (tested_method_id, test_method_id) VALUES(?, ?)
        '''

    @property
    def _link_establishing_sql(self) -> str:
        return '''
        SELECT TESTED_METHODS.id, TEST_METHODS.id FROM (
            (
                SELECT commit_hash, target_method_id AS id FROM main.changes
                WHERE change_type = 'ADD'
                AND EXISTS( 
                    SELECT id FROM methods
                    WHERE id = target_method_id
                    AND file_path LIKE '%src/main/java/org/apache/commons/lang3%'
                )
            ) TESTED_METHODS
            JOIN 
            (
                SELECT commit_hash, target_method_id AS id FROM main.changes
                WHERE change_type = 'ADD'
                AND EXISTS( 
                    SELECT id FROM methods
                    WHERE id = target_method_id
                    AND file_path LIKE '%src/test/java/org/apache/commons/lang3%'
                )
            ) TEST_METHODS
            ON TESTED_METHODS.commit_hash = TEST_METHODS.commit_hash
        )
        '''