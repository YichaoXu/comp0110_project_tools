from establisher.abs_link_builder import AbsLinkEstablisher


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
        alive_methods_table AS (
            SELECT * FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
        ),
        modified_week_table AS (
            SELECT target_method_id, week AS change_week FROM (
                changes JOIN week_commit_table JOIN alive_methods_table
                ON changes.commit_hash = week_commit_table.commit_hash
                AND changes.target_method_id = alive_methods_table.id
                AND change_type = 'MODIFY'
            )
            GROUP BY target_method_id, change_week
        ),
        tested_methods_table AS (
            SELECT id AS tested_id FROM alive_methods_table WHERE file_path LIKE 'src/main/java/%'
        ),
        test_methods_table AS (
            SELECT id AS test_id FROM alive_methods_table WHERE file_path LIKE 'src/test/java/%'
        )
        SELECT tested_id, test_id, COUNT(*) AS Co_change_num FROM (
            tested_methods_table JOIN test_methods_table
            ON EXISTS(
                SELECT change_week FROM modified_week_table WHERE target_method_id = tested_id
                INTERSECT
                SELECT change_week FROM modified_week_table WHERE target_method_id = test_id
            )
        ) GROUP BY tested_id, test_id
        '''