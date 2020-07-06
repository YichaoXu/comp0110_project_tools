# STATEMENT FOR TABLE CHANGE

CREATE_TABLE_FOR_CHANGE = """
    CREATE TABLE if NOT EXISTS {db_name}_changes (
        change_type  VARCHAR(31) NOT NULL, 
        commit_hash VARCHAR(63) NOT NULL, 
        target_method_id INTEGER NOT NULL, 
        CONSTRAINT change_unique 
            UNIQUE (target_method_id, change_type, commit_hash)
        CONSTRAINT relative_to_method  
            FOREIGN KEY (target_method_id) 
            REFERENCES {db_name}_methods(method_id)
    )
"""

INSERT_CHANGE = """
    INSERT INTO {db_name}_changes  (change_type, commit_hash, target_method_id)
        VALUES ('{change_type}', '{commit_hash}', {target_method_id}) 
"""

