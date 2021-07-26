# OpenLookeng性能的自动化测试

主要是对OpenLookeng的clickhouse 连接器进行测试，顺带测着clickhouse进行比对  

其中`auto-ol.json`,`poc-ch.json`，`sql_filter.py`包含了测试用的sql数据，已经剔除原有表名和字段名，仅保留结构

此项目中的OpenLookeng驱动领先于 <https://github.com/jiangph1001/OpenLookeng-driver>

### 目录结构

```
- install.sh         # 安装脚本 （基于xj环境,python2.7）
- run.sh             # 测试脚本
- requirements.txt   # 依赖
- Dockerfile         
- docker-compose.yml 
- (log.tgz)          # 测试运行完后自动生成，基于log文件夹打包
> log 日志目录
  > 2021-*           # OpenLookeng每个sql的查询结果，但目前根据xj环境要求，不能取回数据库的数据，所以在本地分析后即删除，不参与打包
  - install.log      # 安装日志
  - ch-result.log    # ClickHouse运行统计日志
  - ol-result.log    # OpenLookeng运行统计日志
  - ch-*.json        # ClickHouse单次执行详细结果
  - ol-*.json        # OpenLookeng单次执行详细结果
> src
  - auto-ol.json     # OpenLookeng测试语句
  - poc-ch.json      # ClickHouse测试语句
  - config           # 配置文件
  - openlookeng_driver.py  #openlookeng驱动文件
  - run.py           # python自动化测试脚本
  - convert_sql.py   # 根据poc-ch.json生成openlookeng语法的测试集
  - sql_filter.py    # 临时调整测试集为一个子集，筛选需要测试的函数
> whl                # 离线安装包目录
  - clickhouse_driver-0.1.2-cp27-cp27mu-manylinux1_x86_64.whl
  - clickhouse_driver-0.2.1-cp35-cp35m-manylinux1_x86_64.whl
  - requests_toolbelt-0.9.1-py2.py3-none-any.whl
```


## Docker运行
此方法主要因为在测试环境中不能联网pip安装依赖，所以通过docker进行测试
```
docker build -t poc_jph:latest .
./docker_run.sh
```


## 本地运行

```
pip install -r requirements.txt
./run.sh
```

## 结果
等待执行完成后，将自动生成`log.tgz`压缩包，为各种日志的打包

## 运行效果
```
Creating network "xj_default" with the default driver
Creating poc ... done
run explain
running Q1 success , 1√，0×
running Q2 success , 2√，0×
running Q3 success , 3√，0×
running Q4 success , 4√，0×
running Q5 success , 5√，0×
running Q6 success , 6√，0×
running Q7 success , 7√，0×
running Q8 success , 8√，0×
running Q9 success , 9√，0×
running Q10 success , 10√，0×
running explain Q1 success , 1√，0×
running explain Q2 success , 2√，0×
running explain Q3 success , 3√，0×
running explain Q4 success , 4√，0×
running explain Q5 success , 5√，0×
running explain Q6 success , 6√，0×
running explain Q7 success , 7√，0×
running explain Q8 success , 8√，0×
running explain Q9 success , 9√，0×
running explain Q10 success , 10√，0×a ./log
a ./log/2021-07-26-08-34-47
a ./log/explain-2021-07-26-08-34-47.json
a ./log/explain-2021-07-26-08-35-27.json
a ./log/2021-07-26-08-34-47.zip
a ./log/ol-result.log
a ./log/explain-result.log
a ./log/systeminfo.log
a ./log/2021-07-26-08-35-27
a ./log/runtime.log
a ./log/ol-2021-07-26-08-34-47.json
a ./log/ol-2021-07-26-08-35-27.json
a ./log/2021-07-26-08-35-27/Q5.csv
a ./log/2021-07-26-08-35-27/Q4.csv
a ./log/2021-07-26-08-35-27/Q6.csv
a ./log/2021-07-26-08-35-27/Q7.csv
a ./log/2021-07-26-08-35-27/Q3.csv
a ./log/2021-07-26-08-35-27/Q2.csv
a ./log/2021-07-26-08-35-27/Q1.csv
a ./log/2021-07-26-08-35-27/Q10.csv
a ./log/2021-07-26-08-35-27/Q9.csv
a ./log/2021-07-26-08-35-27/Q8.csv
a ./log/2021-07-26-08-34-47/Q5.csv
a ./log/2021-07-26-08-34-47/Q4.csv
a ./log/2021-07-26-08-34-47/Q6.csv
a ./log/2021-07-26-08-34-47/Q7.csv
a ./log/2021-07-26-08-34-47/Q3.csv
a ./log/2021-07-26-08-34-47/Q2.csv
a ./log/2021-07-26-08-34-47/Q1.csv
a ./log/2021-07-26-08-34-47/Q10.csv
a ./log/2021-07-26-08-34-47/Q9.csv
a ./log/2021-07-26-08-34-47/Q8.csv
Stopping poc ... done
Removing poc ... done
Removing network xj_default
FINISH

```