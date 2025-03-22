from sqlalchemy import create_engine, inspect
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from core.database_prod import DATABASE_URL


class SchemaReader:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.engine = self._create_engine()

    def _create_engine(self):
        db_url = (
            f"mysql+pymysql://{self.db_config['user']}:{quote_plus(self.db_config['password'])}"
            f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        )
        return create_engine(
            db_url,
            connect_args={"charset": "utf8mb4", "connect_timeout": 60}
        )

    def get_table_data(self, table_name: str, batch_size: int = 1000):
        import pandas as pd
        
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        total_count = pd.read_sql(count_query, self.engine).iloc[0]['count']
        
        for offset in range(0, total_count, batch_size):
            query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            df = pd.read_sql(query, self.engine)
            yield df.to_dict('records')

def main():
    db_config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'port': '3306',
        'database': 'fake'
    }
    
    reader = SchemaReader(db_config)
    
    table_name = "app_chatmessage"
    for batch in reader.get_table_data(table_name):
        print(f"Batch of {len(batch)} records:")
        for row in batch:
            print(row)
        break 

if __name__ == "__main__":
    main()