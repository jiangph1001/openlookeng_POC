# -*- coding: utf-8 -*-
import clickhouse_driver
import openlookeng_driver
import json,time,logging,sys,os
import configparser,shutil
from sql_filter import *
olconfig = {}
chconfig = {}

time1,time2 = '',''
sql_timeout = 2000
run_loc = './'
datetime_flag = 0
def change_sql(mode,origin_sql):
    changed_sql = origin_sql.replace("$time1","'" + time1 + "'").replace("$time2","'" + time2 + "'")
    return changed_sql


def execute_sql(client,sql):
    start = time.time()
    ans = client.execute(sql)
    end = time.time()
    return end-start

def wc_l(filename):
    try:
        with open(filename,"r") as file:
            content = file.readlines()
        os.remove(filename)
        return len(content)
    except Exception as e:
        return 0

    
def get_current_time():
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

def run_ch(test_sql,now_time = '2021'):
    client = clickhouse_driver.Client(host=chconfig['host'],port=chconfig['port'],user=chconfig['user'] ,password=chconfig['password'])
    results = {}
    total_time = 0
    suc_num,fail_num = 0,0
    client.execute("use tsg_galaxy_v3")
    for k,v in test_sql.items():
        result = {}
        run_sql = change_sql('ch',v)
        result['sql'] = run_sql
        try:
            used_time = execute_sql(client,run_sql)
            if k == 'pre':
                continue
            total_time += used_time
            result['used_time'] = used_time
            result['data_num'] = 0
            result['info'] = ''
            suc_num += 1
            print("running {} success , {}√，{}×".format(k,suc_num,fail_num))
        except Exception as e:
            result['used_time'] = -1
            result['data_num'] = -1
            result['info'] = str(e)
            fail_num += 1
            print("running {} failed  , {}√，{}×  {}".format(k,suc_num,fail_num,result['info'].replace('\n','')[:40]))

        results[k] = result
        try:
            with open(run_loc + "../log/ch-"+now_time + ".json",'w') as file:
                file.write(json.dumps(results))
        except Exception as e:
            print("error",e)
        try:
            file = open(run_loc + "../log/ch-result.log","a+")
            file.write("{} {} success num: {}  failed num: {} \n".format(k,now_time,suc_num,fail_num))
            file.close()
        except Exception as e:
            print(e)
        time.sleep(10)



def run_olk(test_sql,now_time = '2021'):
    client = openlookeng_driver.Client(host=olconfig['host'],port=int(olconfig['port']),user=olconfig['user'],catalog=olconfig['catalog'],schema=olconfig['schema'])
    #client.add_logging(log_level=logging.DEBUG)
    results = {}
    total_time = 0
    suc_num,fail_num = 0,0
    os.mkdir(run_loc + "../log/" + now_time)
    for k,v in test_sql.items():
        result = {}
        run_sql = change_sql('ol',v)
        result['sql'] = run_sql
        try:
            web_result = client.web_execute(run_sql)
            used_time = float(web_result.get_used_time(sql_timeout))  # second
            web_result.download_csv("{}../log/{}/{}.csv".format(run_loc,now_time,str(k)))
            total_time += used_time
            result['used_time'] = used_time
            result['data_num'] = wc_l("{}../log/{}/{}.csv".format(run_loc,now_time,str(k)))
            suc_num += 1
            print("running {} success , {}√，{}×".format(k,suc_num,fail_num))
        except Exception as e:
            result['used_time'] = -1
            result['data_num'] = -1
            result['info'] = str(e)
            fail_num += 1
            print("running {} failed  , {}√，{}× {}".format(k,suc_num,fail_num,result['info'].replace('\n','')[:40]))
        results[k] = result
        try:
            with open(run_loc + "../log/ol-" + now_time + ".json",'w') as file:
                file.write(json.dumps(results))
            with open(run_loc + "../log/ol-result.log","a+") as file:
                file.write("{} {} success num: {}  failed num: {} \n".format(k,now_time,suc_num,fail_num))
        except Exception as e:
            print(e)
    path = "{}../log/{}".format(run_loc,now_time)
    if os.path.exists(path):
        shutil.rmtree(path)
    time.sleep(10)

def run_explain(test_sql,now_time = '2021'):
    client = openlookeng_driver.Client(host=olconfig['host'],port=int(olconfig['port']),user=olconfig['user'],catalog=olconfig['catalog'],schema=olconfig['schema'])
    results = {}
    total_time = 0
    suc_num,fail_num = 0,0
    os.mkdir(run_loc + "../log/" + now_time)
    for k,v in test_sql.items():
        result = {}
        ## add explain
        run_sql = "explain " + change_sql('ol',v)
        result['sql'] = run_sql
        try:
            web_result = client.web_execute(run_sql)
            used_time = float(web_result.get_used_time(sql_timeout))  # second
            web_result.download_csv("{}../log/{}/{}.csv".format(run_loc,now_time,str(k)))
            total_time += used_time
            result['used_time'] = used_time
            suc_num += 1
            print("running explain {} success , {}√，{}×".format(k,suc_num,fail_num))
        except Exception as e:
            result['used_time'] = -1
            result['data_num'] = -1
            result['info'] = str(e)
            fail_num += 1
            print("running explain {} failed  , {}√，{}× {}".format(k,suc_num,fail_num,result['info'].replace('\n','')[:40]))
        results[k] = result
        try:
            with open(run_loc + "../log/explain-" + now_time + ".json",'w') as file:
                file.write(json.dumps(results))
            with open(run_loc + "../log/explain-result.log","a+") as file:
                file.write("{} {} success num: {}  failed num: {} \n".format(k,now_time,suc_num,fail_num))
        except Exception as e:
            print(e)
    time.sleep(10)


def ch_poc():
    with open(run_loc + "poc-ch.json",'r') as file:
        now_time = get_current_time()
        poc = json.loads(file.read())
        # temp solve datetime error issue
        if (datetime_flag):
            poc = test_exclude_toDateTime('ch',poc)
        run_ch(poc,now_time)

def ol_poc():
    with open(run_loc + "auto-ol.json",'r') as file:
        now_time = get_current_time()
        poc = json.loads(file.read())
        if (datetime_flag):
            poc = test_exclude_toDateTime('ol',poc)
        run_olk(poc,now_time)

def explain_poc():
    with open(run_loc + "auto-ol.json",'r') as file:
        now_time = get_current_time()
        poc = json.loads(file.read())
        if (datetime_flag):
            poc = explain_test(poc)
        #run_olk(poc,now_time)
        run_explain(poc,now_time)


def read_conf():
    global time1,time2,sql_timeout,olconfig,chconfig,run_loc,datetime_flag
    # 指定根目录
    if (len(sys.argv) == 3):
        run_loc = sys.argv[2] + "/src/"
    config = configparser.ConfigParser()
    config.read(run_loc + "config")

    time1 = config.get("run","time1")
    time2 = config.get("run","time2")
    
    sql_timeout = config.get("run","time_out") # default 900s 15min

    ch_sector = "clickhouse"
    ol_sector = "openlookeng"

    chconfig['host'] = config.get(ch_sector,"host")
    chconfig['port'] = str(config.get(ch_sector,"port"))
    chconfig['user'] = config.get(ch_sector,"user")
    chconfig['password'] = str(config.get(ch_sector,"password"))

    olconfig['host'] = config.get(ol_sector,"host")
    olconfig['port'] = str(config.get(ol_sector,"port"))
    olconfig['user'] = config.get(ol_sector,"user")
    olconfig['catalog'] = config.get(ol_sector,"catalog")
    olconfig['schema'] = config.get(ol_sector,"schema")
    datetime_flag = config.get("optional","list_without_datetime")

def check_connect():
    pass

if __name__ == "__main__":
    read_conf()
    if sys.argv[1] == 'ch':
        print("run ch")
        ch_poc()
    elif sys.argv[1] == 'ol':
        print("run ol")
        ol_poc()
    elif sys.argv[1] == 'explain':
        print("run explain")
        explain_poc()
    else:
        print("error")

    
        
