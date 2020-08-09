from sql2link.establisher import AbsLinkEstablisher


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
            confidence_num INTEGER,
            FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
            FOREIGN KEY (test_method_id) REFERENCES methods(id)
        );
        '''

    @property
    def _insert_new_row_sql(self) -> str:
        return '''
        INSERT INTO co_created_for_commits (tested_method_id, test_method_id, confidence_num) VALUES(?, ?, 1)
        '''

    @property
    def _link_establishing_sql(self) -> str:
        return '''
        WITH alive_methods AS (
            SELECT id, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
            AND simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE (class_name || '%') AND simple_name NOT LIKE ('for(int i%')
        ), tested_methods AS (
            SELECT alive_methods.id AS tested_method_id, commit_hash FROM alive_methods, changes
            WHERE file_path LIKE 'src/main/java/org/apache/commons/lang3/%'
            AND change_type = 'ADD' AND alive_methods.id = changes.target_method_id
        ), test_methods AS (
            SELECT alive_methods.id AS test_method_id, commit_hash FROM alive_methods, changes
            WHERE file_path LIKE 'src/test/java/org/apache/commons/lang3/%'
            AND change_type = 'ADD' AND alive_methods.id = changes.target_method_id
        )
        SELECT tested_method_id, test_method_id FROM (
            test_methods INNER JOIN tested_methods
            ON test_methods.commit_hash = tested_methods.commit_hash
        )
        '''
