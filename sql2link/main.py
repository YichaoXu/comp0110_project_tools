import sqlite3


SELECT_CO_CREATED_METHODS_SQL = '''
    SELECT TESTED_METHODS.id, TEST_METHODS.id FROM (
        (
            SELECT commit_hash, target_method_id AS id FROM changes
            WHERE change_type = 'ADD'
            AND EXISTS( 
                SELECT id FROM methods
                WHERE id = target_method_id
                AND file_path LIKE '%src/main/java/org/apache/commons/lang3%'
            )
        ) TESTED_METHODS
        JOIN 
        (
            SELECT commit_hash, target_method_id AS id FROM changes
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

CREATE_STRATEGY_01_TABLE_SQL = '''
    CREATE TABLE strategy01 (
        tested_method_id INTEGER NOT NULL,
        test_method_id INTEGER NOT NULL,
        score FLOAT NOT NULL,
        FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
        FOREIGN KEY (test_method_id) REFERENCES methods(id)
    );
'''

INSERT_NEW_ROW_FOR_STRATEGY_01_TABLE_SQL = '''
    INSERT INTO strategy01 (tested_method_id, test_method_id, score) 
    VALUES(?, ?, 1.0)
'''


def strategy_one(path: str, name: str):
    db_path = f'{path}/{name}.db'
    db_path = db_path.replace('-', '_')
    connector = sqlite3.connect(db_path)
    cursor = connector.cursor()
    cursor.execute(CREATE_STRATEGY_01_TABLE_SQL)
    cursor.execute(SELECT_CO_CREATED_METHODS_SQL)
    for row in cursor.fetchall():
        cursor.execute(INSERT_NEW_ROW_FOR_STRATEGY_01_TABLE_SQL, row)
    cursor.close()
    connector.commit()


SELECT_CO_CHANGED_METHODS_SQL = '''
SELECT tested_id, test_id, support_num, CAST(support_num AS FLOAT)/all_changes_num AS confidence_num FROM
(
    SELECT tested_id, test_id, COUNT(*) AS support_num FROM
    (
        SELECT target_method_id AS tested_id, commit_hash FROM changes
        WHERE change_type = 'MODIFY'
        AND EXISTS(
            SELECT id
            FROM methods
            WHERE id = tested_id
            AND file_path LIKE '%src/main/java/org/apache/commons/lang3%'
        )
    ) TESTED,
    (
        SELECT target_method_id AS test_id, commit_hash FROM changes
        WHERE change_type = 'MODIFY'
        AND EXISTS(
            SELECT id FROM methods
            WHERE id = test_id
            AND file_path LIKE '%src/test/java/org/apache/commons/lang3%'
        )
    ) TEST
    WHERE TESTED.commit_hash = TEST.commit_hash
    GROUP BY tested_id, test_id
) COCHANGE
,(
    SELECT target_method_id AS count_id, COUNT(commit_hash) AS all_changes_num FROM changes
    WHERE change_type = 'MODIFY'
    AND EXISTS(
        SELECT id FROM methods
        WHERE id = count_id
        AND file_path LIKE '%src/main/java/org/apache/commons/lang3%'
    )
    GROUP BY count_id
) ALLCHANGE
WHERE COCHANGE.tested_id = ALLCHANGE.count_id
'''

CREATE_STRATEGY_02_TABLE_SQL = '''
    CREATE TABLE strategy02 (
        tested_method_id INTEGER NOT NULL,
        test_method_id INTEGER NOT NULL,
        support_num INTEGER NOT NULL,
        confidence_num FLOAT NOT NULL,
        FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
        FOREIGN KEY (test_method_id) REFERENCES methods(id)
    );
'''

INSERT_NEW_ROW_FOR_STRATEGY_02_TABLE_SQL = '''
    INSERT INTO strategy02 (tested_method_id, test_method_id, support_num, confidence_num) 
    VALUES(?, ?, ?, ?)
'''


def strategy_two(path: str, name: str):
    db_path = f'{path}/{name}.db'
    db_path = db_path.replace('-', '_')
    connector = sqlite3.connect(db_path)
    cursor = connector.cursor()
    cursor.execute(CREATE_STRATEGY_02_TABLE_SQL)
    cursor.execute(SELECT_CO_CHANGED_METHODS_SQL)
    for row in cursor.fetchall():
        cursor.execute(INSERT_NEW_ROW_FOR_STRATEGY_02_TABLE_SQL, row)
    cursor.close()
    connector.commit()


SELECT_APRIORI_ALGORITHM_SQL = '''
WITH frequent_unique_table AS (
    SELECT target_method_id AS id, COUNT(commit_hash) AS support FROM changes
    WHERE change_type = 'MODIFY' GROUP BY target_method_id HAVING support > :min_support_for_change
),
frequent_test_table AS (
    SELECT id AS test_id, support AS test_support FROM frequent_unique_table
    WHERE EXISTS( 
        SELECT id FROM methods 
        WHERE id = test_id 
        AND file_path LIKE '%src/test/java/org/apache/commons/lang3%' 
    )
),
frequent_tested_table AS (
    SELECT id AS tested_id, support AS tested_support FROM frequent_unique_table
    WHERE EXISTS( 
        SELECT id FROM methods 
        WHERE id = tested_id 
        AND file_path LIKE '%src/main/java/org/apache/commons/lang3%' 
    )
),
frequent_test_commits AS (
    SELECT commit_hash AS test_commit_hash, test_id, test_support
    FROM changes, frequent_test_table
    WHERE target_method_id = test_id
),
frequent_tested_commits AS (
    SELECT commit_hash AS tested_commit_hash, tested_id, tested_support
    FROM changes, frequent_tested_table
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

CREATE_STRATEGY_03_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS strategy03 (
        tested_method_id INTEGER NOT NULL,
        test_method_id INTEGER NOT NULL,
        support_num INTEGER NOT NULL,
        confidence_num FLOAT NOT NULL,
        FOREIGN KEY (tested_method_id) REFERENCES methods(id), 
        FOREIGN KEY (test_method_id) REFERENCES methods(id)
    );
'''

INSERT_NEW_ROW_FOR_STRATEGY_03_TABLE_SQL = '''
    INSERT INTO strategy03 (tested_method_id, test_method_id, support_num, confidence_num) 
    VALUES(?, ?, ?, ?)
'''


def strategy_three(path: str, name: str):
    db_path = f'{path}/{name}.db'
    db_path = db_path.replace('-', '_')
    connector = sqlite3.connect(db_path)
    cursor = connector.cursor()
    cursor.execute(CREATE_STRATEGY_03_TABLE_SQL)
    cursor.execute(SELECT_APRIORI_ALGORITHM_SQL, {
        'min_support_for_change': 70,
        'min_support_for_cochange': 60,
        'min_confidence': 0.4
    })
    for row in cursor.fetchall():
        cursor.execute(INSERT_NEW_ROW_FOR_STRATEGY_03_TABLE_SQL, row)
    cursor.close()
    connector.commit()