import mysql.connector
import os
from collections import defaultdict

# 连接到MySQL数据库
conn = mysql.connector.connect(
    host='',
    user='',
    password='',
    database=''
)

cursor = conn.cursor()

# 查询field_name、value_type和taos_stable字段并去重
query = "SELECT DISTINCT field_name, value_type, taos_stable FROM sys_cld_point_cfg"
cursor.execute(query)

# 获取查询结果
field_info = cursor.fetchall()

# 关闭数据库连接
cursor.close()
conn.close()

# 分组字段定义语句
groups = defaultdict(list)
seen_field_names = set()

for field_name, value_type, taos_stable in field_info:
    group_key = taos_stable
    groups[group_key].append((field_name, value_type))
    seen_field_names.add(field_name)

# 统计创建表的信息
table_count = 0
table_field_counts = {}
sql_statements = []
insert_statements = []
java_methods = []
entity_classes = []

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def to_camel_case_class_name(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def java_type(value_type):
    return 'boolean' if value_type.lower() == 'bool' else value_type

# 创建用于存放 Java 实体类文件的文件夹
os.makedirs("entities", exist_ok=True)

# 生成每个组的TDengine创建表语句、insert语句、Java方法声明和实体类
for group, fields in groups.items():
    if fields and not group.startswith('DG'):
        table_count += 1
        field_count = len(fields)
        table_field_counts[group] = field_count

        tdengine_create_table = """
        USE yuyou_shore;

        CREATE STABLE {} (
            ts TIMESTAMP,
            {}
        ) TAGS (
            ship_code NCHAR(30),
            unique_index NCHAR(20)
        );
        """.format(group, ",\n    ".join(f"{field_name} {value_type}" for field_name, value_type in fields))

        sql_statements.append(tdengine_create_table)

        insert_id = to_camel_case(f"add_{group}")

        insert_statement = """
<insert id="{}">
    insert into {}_#{{shipCode}}_#{{suffix}} using {} TAGS (#{{shipCode}}, #{{uniqueIndex}})
    values (
        #{{ts}},
        {}
    )
</insert>
""".format(insert_id, group, group, ",\n        ".join(f"#{{{to_camel_case(field)}}}" for field, _ in fields))

        insert_statements.append(insert_statement)

        java_method = "int {}({} {});".format(insert_id, to_camel_case_class_name(group), to_camel_case(group))
        java_methods.append(java_method)

        class_name = to_camel_case_class_name(group)
        entity_class = """
package com.yuyou.taos.domain;

import lombok.Data;

/**
 * 超级表 {}
 * 作者: YangKai
 * 时间: 2024/6/14 15:10
 */
@Data
public class {} extends TaosBaseEntity {{

    {}
}}
""".format(group, class_name, "\n\n    ".join(f"private {java_type(value_type)} {to_camel_case(field_name)};" for field_name, value_type in fields))

        entity_classes.append((class_name, entity_class))

# 写入SQL到txt文件
with open("tdengine_create_tables.sql", "w", encoding='utf-8') as file:
    for statement in sql_statements:
        file.write(statement)
        file.write("\n")

# 写入Insert语句到txt文件
with open("tdengine_insert_statements.xml", "w", encoding='utf-8') as file:
    for statement in insert_statements:
        file.write(statement)
        file.write("\n")

# 写入Java方法到txt文件
with open("java_methods.txt", "w", encoding='utf-8') as file:
    for method in java_methods:
        file.write(method)
        file.write("\n")

# 写入实体类到各自的Java文件
for class_name, entity_class in entity_classes:
    with open(f"entities/{class_name}.java", "w", encoding='utf-8') as file:
        file.write(entity_class)

# 打印总结信息
print(f"总共创建了 {table_count} 张表。")
for group, field_count in table_field_counts.items():
    print(f"表 {group} 有 {field_count} 个字段。")
