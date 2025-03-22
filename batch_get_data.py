from sqlalchemy import create_engine, inspect
from typing import Dict, List, Optional
from urllib.parse import quote_plus


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

    def get_table_schema(self, table_name: Optional[str] = None) -> Dict[str, List[Dict]]:
        inspector = inspect(self.engine)
        schema_info = {}

        if table_name:
            tables = [table_name]
        else:
            tables = inspector.get_table_names()

        for tbl in tables:
            columns = []
            for column in inspector.get_columns(tbl):
                column_info = {
                    'name': column['name'],
                    'type': str(column['type']),
                    'nullable': column.get('nullable', True),
                    'default': column.get('default', None),
                    'primary_key': column.get('primary_key', False)
                }
                columns.append(column_info)
            
            foreign_keys = []
            for fk in inspector.get_foreign_keys(tbl):
                foreign_keys.append({
                    'constrained_columns': fk['constrained_columns'],
                    'referred_table': fk['referred_table'],
                    'referred_columns': fk['referred_columns']
                })
            
            schema_info[tbl] = {
                'columns': columns,
                'foreign_keys': foreign_keys
            }

        return schema_info

    def print_schema(self, table_name: Optional[str] = None):
        """Print formatted schema information"""
        schema = self.get_table_schema(table_name)
        
        for table_name, info in schema.items():
            print(f"\n=== Table: {table_name} ===")
            print("\nColumns:")
            for col in info['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                pk = "PRIMARY KEY" if col['primary_key'] else ""
                default = f"DEFAULT {col['default']}" if col['default'] else ""
                print(f"- {col['name']}: {col['type']} {nullable} {default} {pk}")
            
            if info['foreign_keys']:
                print("\nForeign Keys:")
                for fk in info['foreign_keys']:
                    print(f"- {', '.join(fk['constrained_columns'])} -> "
                          f"{fk['referred_table']}({', '.join(fk['referred_columns'])})")

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
    
    table_name = "app_categorygroup"
    for batch in reader.get_table_data(table_name):
        print(f"Batch of {len(batch)} records:")
        for row in batch:
            print(row)
        break 

if __name__ == "__main__":
    main()