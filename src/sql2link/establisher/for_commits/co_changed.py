from sql2link.establisher import AbsLinkEstablisher


class CoChangedInCommitLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str: return '''
        DROP TABLE IF EXISTS links_commits_based_cochanged
    '''

    @property
    def _initial_table_sql(self) -> str: return '''
        CREATE TABLE links_commits_based_cochanged (
            tested_method_id INTEGER NOT NULL,
            test_method_id INTEGER NOT NULL,
            support_num INTEGER NOT NULL,
            confidence_num FLOAT NOT NULL,
            FOREIGN KEY (tested_method_id) REFERENCES git_methods(id), 
            FOREIGN KEY (test_method_id) REFERENCES git_methods(id)
        );
    '''

    @property
    def _insert_new_row_sql(self) -> str:
        return '''
        INSERT INTO links_commits_based_cochanged (
            tested_method_id, 
            test_method_id, 
            support_num, 
            confidence_num
        )  VALUES(?, ?, ?, ?)
        '''

    @property
    def _link_establishing_sql(self) -> str: return '''
        WITH valid_methods AS (
            SELECT id, file_path FROM git_methods
            WHERE simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE ('for(int i%')
        ), tested_methods AS (
            SELECT valid_methods.id AS tested_method_id, commit_hash FROM (
                git_changes  INNER JOIN valid_methods
                ON valid_methods.id = git_changes.target_method_id
            )
            WHERE file_path LIKE 'src/main/java/org/apache/commons/lang3/%'
        ), test_methods AS (
            SELECT valid_methods.id AS test_method_id, commit_hash FROM (
                git_changes INNER JOIN valid_methods
                ON valid_methods.id = git_changes.target_method_id
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
