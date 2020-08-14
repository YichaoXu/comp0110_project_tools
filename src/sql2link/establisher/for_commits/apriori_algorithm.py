from sql2link.establisher import AbsLinkEstablisher


class AprioriInCommitLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str:
        return '''
        DROP TABLE IF EXISTS links_commits_based_apriori
        '''

    @property
    def _initial_table_sql(self) -> str:
        return '''
        CREATE TABLE links_commits_based_apriori (
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
        INSERT INTO links_commits_based_apriori (
            tested_method_id, 
            test_method_id, 
            support_num, 
            confidence_num
        ) VALUES(?, ?, ?, ?)
        '''

    @property
    def _link_establishing_sql(self) -> str: return '''
        WITH valid_methods AS (
            SELECT id, file_path FROM methods
            WHERE simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE ('for(int i%')
        ), frequent_unique_table AS (
            SELECT target_method_id AS id, COUNT(commit_hash) AS support FROM changes 
            WHERE EXISTS(
                SELECT id FROM valid_methods WHERE target_method_id = id
            ) GROUP BY target_method_id
        ),
        frequent_test_table AS (
            SELECT id AS test_id, support AS test_support FROM frequent_unique_table
            WHERE EXISTS( 
                SELECT id FROM methods 
                WHERE id = test_id AND file_path LIKE  'src/test/java/org/apache/commons/lang3/%'
            ) 
        ),
        frequent_tested_table AS (
            SELECT id AS tested_id, support AS tested_support FROM frequent_unique_table
            WHERE EXISTS( 
                SELECT id FROM methods 
                WHERE id = tested_id AND file_path LIKE 'src/main/java/org/apache/commons/lang3/%'
            ) 
            AND support > :min_support_for_change
        ),
        frequent_test_commits AS (
            SELECT commit_hash AS test_commit_hash, test_id, test_support
            FROM changes , frequent_test_table
            WHERE target_method_id = test_id
        ),
        frequent_tested_commits AS (
            SELECT commit_hash AS tested_commit_hash, tested_id, tested_support
            FROM changes , frequent_tested_table
            WHERE target_method_id = tested_id
        ),
        frequent_cochange_table AS(
            SELECT tested_id, test_id, COUNT(*) AS cochange_support, test_support FROM (
                frequent_test_commits JOIN frequent_tested_commits
                ON test_commit_hash = tested_commit_hash
            )GROUP BY tested_id, test_id
            HAVING cochange_support > :min_support_for_cochange
        )
        
        SELECT tested_id, test_id, cochange_support, CAST(cochange_support AS FLOAT)/test_support AS confidence
        FROM frequent_cochange_table
        WHERE confidence > :min_confidence
        '''
