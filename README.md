# GenerateTDengineJavaFiles

## 描述

这个Python脚本的主要作用是从MySQL数据库中提取字段信息，生成TDengine数据库表创建语句、Insert语句、Java方法声明和Java实体类文件，并将生成的内容保存到相应的文件中。脚本的主要步骤包括：

1. 连接到MySQL数据库并查询字段信息。
2. 对字段信息进行分组和处理。
3. 生成TDengine创建表的SQL语句。
4. 生成TDengine的Insert语句。
5. 生成Java方法声明。
6. 生成Java实体类文件并将其保存到指定文件夹。
7. 输出生成表的统计信息。

## 输出文件

- `tdengine_create_tables.sql`：保存生成的TDengine创建表SQL语句。
- `tdengine_insert_statements.xml`：保存生成的TDengine Insert语句。
- `java_methods.txt`：保存生成的Java方法声明。
- `entities`文件夹：保存生成的Java实体类文件。

## 使用方法

1. 确保你已经安装了必要的Python库：
   ```bash
   pip install mysql-connector-python
