from sql2link.establisher import AbsLinkEstablisher


class CoChangedtedInAllChangeTypeFilteredCommitLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str: return '''
        DROP TABLE IF EXISTS links_filtered_commits_based_cochanged
    '''

    @property
    def _initial_table_sql(self) -> str: return '''
        CREATE TABLE links_filtered_commits_based_cochanged (
            tested_method_id INTEGER NOT NULL,
            test_method_id INTEGER NOT NULL,
            support INTEGER NOT NULL, 
            confidence_num INTEGER,
            FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
            FOREIGN KEY (test_method_id) REFERENCES methods(id)
        );
    '''

    @property
    def _insert_new_row_sql(self) -> str: return '''
        INSERT INTO links_filtered_commits_based_cochanged (
            tested_method_id, test_method_id, support, confidence_num
        ) VALUES(?, ?, ?, ?)
    '''

    @property
    def _link_establishing_sql(self) -> str: return '''
        WITH commits_changes_count AS (
            SELECT commit_hash, change_type, COUNT(*) AS change_count FROM changes
            GROUP BY commit_hash, change_type
        ),
        invalid_commits AS (
            SELECT DISTINCT commit_hash FROM commits_changes_count
            WHERE (change_type == 'ADD' AND change_count > :add_count_limits)
            OR (change_type == 'MODIFY' AND change_count > :modify_count_limits)
            OR (change_type == 'RENAME' AND change_count > :rename_count_limits)
        ), filtered_change AS (
            SELECT * FROM changes
            WHERE commit_hash NOT IN invalid_commits
        ), valid_methods AS (
            SELECT id, file_path FROM methods
            WHERE simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE ('for(int i%')
        ), tested_methods AS (
            SELECT valid_methods.id AS tested_method_id, commit_hash FROM (
        filtered_change INNER JOIN valid_methods
        ON valid_methods.id = filtered_change.target_method_id
            )
            WHERE file_path LIKE 'src/main/java/org/apache/commons/lang3/%'
        ), test_methods AS (
            SELECT valid_methods.id AS test_method_id, commit_hash FROM (
        filtered_change INNER JOIN valid_methods
        ON valid_methods.id = filtered_change.target_method_id
            )
            WHERE valid_methods.file_path LIKE 'src/test/java/org/apache/commons/lang3/%'
        ), tested_change_count AS (
            SELECT tested_method_id AS count_id, COUNT(tested_method_id) AS change_num FROM tested_methods
            GROUP BY tested_method_id
        ), co_change_table AS (
            SELECT tested_method_id, test_method_id, COUNT(*) AS support FROM (
        tested_methods INNER JOIN test_methods
        ON test_methods.commit_hash = tested_methods.commit_hash
            )
            GROUP BY tested_method_id, test_method_id
        )
        SELECT tested_method_id, test_method_id, support, CAST(support AS FLOAT)/change_num AS confidence FROM (
            co_change_table INNER JOIN tested_change_count
            ON tested_method_id = count_id
        )
    '''
