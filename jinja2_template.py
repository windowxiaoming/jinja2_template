#!/usr/bin/env python
import json
import os
import re
from jinja2 import Environment, FileSystemLoader

# reload(sys)
# sys.setdefaultencoding('utf-8')

def general_json_slow_log_report(json_file):
        f = open(json_file, 'ra')
        format_dict_all_data = json.load(f)
        have_slow_query_tables = []
        all_sql_info = []
        all_slow_query_sql_info = format_dict_all_data['classes']
        global_sql_info = format_dict_all_data['global']

        for slow_query_sql in all_slow_query_sql_info:
            try:
                query_metrics = slow_query_sql['metrics']
                query_time = query_metrics['Query_time']
                query_tables = slow_query_sql['tables']

                for show_tables_sql in query_tables:
                    get_table_name = show_tables_sql['create'].split('.')[1]
                    table_name = re.match(r'`(\w*)`\\G', get_table_name).group(1)
                    if table_name not in have_slow_query_tables:
                        have_slow_query_tables.append(table_name)
            except:
                pass

            sql_info = {
                'ID': slow_query_sql['checksum'],
                'query_time_max': query_time['max'],
                'query_time_min': query_time['min'],
                'query_time_95': query_time['pct_95'],
                'query_time_median': query_time['median'],
                'query_row_send_95': query_metrics['Rows_sent']['pct_95'],
                'query_db': query_metrics['db']['value'],
                'slow_query_count': slow_query_sql['query_count'],
                'slow_query_tables': have_slow_query_tables,
                'sql': slow_query_sql['example']['query'],

            }

            all_sql_info.append(sql_info)
            all_sql_info = sorted(all_sql_info, key=lambda e: float(e['query_time_95']), reverse=True)
        return all_sql_info




if __name__ == "__main__":
    sql_info = general_json_slow_log_report("1.json")

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template("template1.html")
    html_content = template.render(sql_info=sql_info)
    with open("1.html", 'wa') as f:
        f.write(html_content.encode('utf-8'))

