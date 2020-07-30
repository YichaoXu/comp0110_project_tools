from establisher.abs_link_builder import AbsLinkEstablisher


class CoChangedInCommitLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str:
        return '''
        DROP TABLE IF EXISTS co_changed_for_commits
        '''

    @property
    def _initial_table_sql(self) -> str:
        return '''
        CREATE TABLE co_changed_for_commits (
            tested_method_id INTEGER NOT NULL,
            test_method_id INTEGER NOT NULL,
            support_num INTEGER NOT NULL,
            confidence_num FLOAT NOT NULL,
            FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
            FOREIGN KEY (test_method_id) REFERENCES methods(id)
        );
        '''

    @property
    def _insert_new_row_sql(self) -> str:
        return '''
        INSERT INTO co_changed_for_commits (
            tested_method_id, 
            test_method_id, 
            support_num, 
            confidence_num
        )  VALUES(?, ?, ?, ?)
        '''

    @property
    def _link_establishing_sql(self) -> str:
        return '''
        WITH modify_table AS (
            SELECT target_method_id AS id, COUNT(commit_hash) AS support FROM main.changes
            WHERE change_type = 'MODIFY' GROUP BY target_method_id
        ),
        modify_test_table AS (
            SELECT id AS test_id, support AS test_support FROM modify_table
            WHERE EXISTS(
                SELECT id FROM methods
                WHERE id = test_id
                AND file_path LIKE 'src/test%'
            )
        ),
        modify_tested_table AS (
            SELECT id AS tested_id, support AS tested_support FROM modify_table
            WHERE EXISTS(
                SELECT id FROM methods
                WHERE id = tested_id
                AND file_path LIKE 'src/main%'
            )
        ),
        modify_test_commits AS (
            SELECT commit_hash AS test_commit_hash, test_id, test_support
            FROM changes, modify_test_table
            WHERE target_method_id = test_id
        ),
        modify_tested_commits AS (
            SELECT commit_hash AS tested_commit_hash, tested_id, tested_support
            FROM changes, modify_tested_table
            WHERE target_method_id = tested_id
        ),
        frequent_cochange_table AS(
            SELECT tested_id, test_id, COUNT(*) AS cochange_support, test_support FROM (
                modify_test_commits JOIN modify_tested_commits
                ON test_commit_hash = tested_commit_hash
            )GROUP BY tested_id, test_id
        )
        SELECT tested_id, test_id, cochange_support, CAST(cochange_support AS FLOAT)/test_support AS confidence
        FROM frequent_cochange_table
        '''