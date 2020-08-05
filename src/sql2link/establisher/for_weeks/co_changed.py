from sql2link.establisher import AbsLinkEstablisher


class CoChangedInWeekLinkEstablisher(AbsLinkEstablisher):

    def __init__(self, db_path: str):
        super().__init__(db_path)

    @property
    def _remove_previous_table_sql(self) -> str:
        return '''
        DROP TABLE IF EXISTS co_changed_for_weeks
        '''

    @property
    def _initial_table_sql(self) -> str:
        return '''
        CREATE TABLE co_changed_for_weeks (
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
        INSERT INTO co_changed_for_weeks (
            tested_method_id, 
            test_method_id, 
            support_num, 
            confidence_num
        )  VALUES(?, ?, ?, ?)
        '''

    @property
    def _link_establishing_sql(self) -> str:
        return '''
        WITH week_commit_table AS (
            SELECT STRFTIME('%Y-%W', commit_date)  AS week, hash_value AS commit_hash  FROM git_commits
        ),
        alive_methods AS (
            SELECT id, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
            AND simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE (class_name || '%') AND simple_name NOT LIKE ('for(int i%')
        ),
        modified_week_table AS (
            SELECT target_method_id, week AS change_week, file_path FROM (
                changes JOIN week_commit_table JOIN alive_methods
                ON changes.commit_hash = week_commit_table.commit_hash
                AND changes.target_method_id = alive_methods.id
            )
            GROUP BY target_method_id, change_week
        ),
        tested_modified AS (
            SELECT target_method_id AS tested_method_id, change_week FROM modified_week_table
            WHERE file_path LIKE 'src/main/java/org/apache/commons/lang3/%'
        ),
        test_modified AS (
            SELECT target_method_id AS test_method_id, change_week FROM modified_week_table
            WHERE file_path LIKE 'src/test/java/org/apache/commons/lang3/%'
        ),
        tested_count AS (
            SELECT tested_method_id, COUNT(*) AS changed_count FROM tested_modified
            GROUP BY tested_method_id
        ),
        co_changed AS (
            SELECT tested_method_id, test_method_id, COUNT(*) AS support FROM (
                tested_modified INNER JOIN test_modified
                ON test_modified.change_week = tested_modified.change_week
            ) GROUP BY tested_method_id, test_method_id
        )
        SELECT co_changed.tested_method_id, test_method_id, support, CAST(support AS FLOAT)/changed_count AS confidence 
        FROM (
            co_changed INNER JOIN tested_count
            ON co_changed.tested_method_id = tested_count.tested_method_id
        )

        '''