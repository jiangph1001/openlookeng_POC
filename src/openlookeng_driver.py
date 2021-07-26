# -*- coding: utf-8 -*-
import requests,json,time,math,re,logging
from datetime import datetime
from requests_toolbelt import MultipartEncoder

class Result:
    def __init__(self,nextUri,timeout = 5):
        self.__nextUri = nextUri
        self.timeout = timeout
        self.infoUri = None
        self.__response = None
        self.__status = None
        self.__used_time = None
    
    def __prettify_response(self,response):
        if self.__status == 'FAILED':
            return "{} {}".format("FAILED",response['error']['message'])
        elif self.__status == 'FINISHED':
            column_name = ""
            for col in response['columns']:
                column_name += col['name']
                column_name += '\t'
            if 'data' in response:
                return "{} \n{}\n{}".format(self.__status,column_name,response['data'])
            return "{} \n{}".format(self.__status,column_name)
    
    def __get_result_immediately(self):
        response = requests.get(self.__nextUri)
        response_dict = json.loads(response.text)
        if 'nextUri' not in response_dict:
            self.__response = response_dict
            self.__status = response_dict['stats']['state']
            self.infoUri = response_dict['infoUri']
            return response_dict
        else:
            self.__nextUri = response_dict['nextUri']
            return None
        
    def get_result(self,timeout = None):
        # 获取执行结果，直到超时
        if self.__response is not None:
            return self.__response
        if timeout is None:
            timeout = self.timeout
        use_time = 0
        interval = 0.5
        while True:
            result = self.__get_result_immediately()
            if result is not None:
                return result
            if use_time > timeout:
                break
            use_time += interval
            time.sleep(interval)
            interval = math.ceil(use_time/10)
        return None
        
    def print_result(self):
        response = self.get_result()
        print(self.__prettify_response(response))

    def get_used_time(self,timeout = None):
        if self.__used_time is not None:
            return self.__used_time
        response = self.get_result(timeout)
        if self.__status == "FINISHED":
            elapsedTimeMillis = response['stats']['elapsedTimeMillis']
        else:
            print(response['error']['message'])
            return 0
        return elapsedTimeMillis
    def get_infoUri(self,timeout = None):
        self.get_result(time)
        return self.infoUri

# web api
class WebResult:
    def __init__(self,sql,uuid,Client,logger):
        self.sql = sql
        self.uuid = uuid
        self.client = Client
        self.result = None
        self.finished = False # 没运行完和执行失败时都是False
        self.used_time = None
        self.infoUri = None
        self.csv_path = None
        self.logger = logger
        self.error_info = ''
    def write_log(self,level = 'info',message = ''):
        if self.logger is None:
            return 
        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'error':
            self.logger.error(message)

    # 尝试获取结果
    def __get_result_immediately(self):
        # 返回当前执行的状态 
        result = self.client.get_query(self.uuid)
        if result is not None:
            #print(result)
            if result['state'] == 'FINISHED':
                self.finished = True
                self.used_time = result['queryStats']['elapsedTime']
                self.infoUri = "http://{}:{}/ui/{}".format(self.client.host,self.client.port,result['infoUri'])
                self.write_log('debug',"SQL : "+self.sql)
                self.write_log('info','FINISHED {} {}'.format(self.used_time,self.infoUri))
            elif result['state'] == 'FAILED':
                #print(result['error']['message'])
                self.error_info = result['error']['message']
                self.write_log('error',"SQL : "+self.sql)
                self.write_log('error',result['error']['message'])
                raise Exception("State Failed: {}".format(self.error_info))
            else:
                return None
        return result
    
    # 一直尝试获取结果，直到超时       
    def get_result(self,timeout = None):
        if self.result is not None:
            return self.result
        if timeout is None:
            timeout = 5
        else:
            timeout = int(timeout)
        elapsed = 0
        started_at = datetime.now()
        interval = 0.5
        while True:
            result = self.__get_result_immediately()
            if result is not None:
                self.result = result
                return result
            if elapsed > timeout:
                break
            now = datetime.now()
            elapsed = (now - started_at).total_seconds()
            time.sleep(interval)
            interval = math.ceil(elapsed/10)
        raise Exception("Timeout {} > {}".format(elapsed,timeout))

    def get_used_time(self,timeout = None):
        self.get_result(timeout)
        if self.used_time is None:
            return 0
        if "ms" in self.used_time:
            return float(re.sub("ms","",self.used_time))/1000
        elif "s" in self.used_time:
            return  float(re.sub("s","",self.used_time))
        else:
            return  float(re.sub("m","",self.used_time))*60
        
    def get_infoUri(self,timeout = None):
        self.get_result(timeout)
        return self.infoUri
    
    def get_output(self,timeout = None):
        csv_path = self.get_csv_path(timeout = None)
        if csv_path is not None:
            print_csv(csv_path)
        
    def get_csv_path(self,timeout = None):
        if self.csv_path is not None:
            return self.csv_path
        self.get_result(timeout)
        if self.finished is False:
            return None
        elif self.result['output']['type'] == 'csv':
            self.csv_path = "http://{}:{}{}".format(self.client.host,self.client.port,self.result['output']['location'][2:])
            return self.csv_path
        else:
            print("output is {} Type".format(self.result['output']['type']))
            return None
    
    def download_csv(self,csv_name = None):
        csv_path = self.get_csv_path(timeout = None)
        if csv_path is not None:
            if csv_name is None:
                csv_name = csv_path.split('/')[-1]
            response = requests.get(csv_path,headers = self.client.headers)
            if response.status_code == 200:
                content = response.content
                with open(csv_name,'wb') as file:
                    file.write(content)
            else:
                raise Exception("Download Error:status code: {}".format(response.status_code))
        else:
            raise Exception("Download Error:csv_path none")
                        
def print_csv(csv_path):
    response = requests.get(csv_path)
    if response.status_code == 200:
        content = response.content.decode().strip()
        lines = content.split('\n')
        print_seperator = True
        for line in lines:
            print(line.replace('"','').replace(',',' | '))
            if print_seperator:
                print_seperator = False
                length = len(line)
                print("-"*length)
    else:
        raise Exception("error: status code: {}".format(response.status_code))
    
class Client:
    def __init__(self,host="127.0.0.1",port=8080,user="lk",catalog="system",schema="runtime",timeout = 10000):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.catalog = catalog
        self.user = user
        self.schema = schema
        self.execute_url = "http://{}:{}{}".format(self.host,self.port,"/v1/statement")
        self.web_execute_url = "http://{}:{}{}".format(self.host,self.port,"/api/execute")
        self.get_history_url = "http://{}:{}{}".format(self.host,self.port,"/api/query/history")
        self.login()
        self.headers = {
            "X-Presto-Catalog":catalog,
            "X-Presto-Schema":schema,
            "X-Presto-User":user,
            "X-Presto-Source":"python_driver",
            "source":"python_web_driver",
            "Content-Type":"application/json"
        }
        #self.headers['Cookie'] = 'Presto-UI-Token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyb290IiwiZXhwIjoxNjE5MDg2NDA1LCJhdWQiOiJwcmVzdG8tdWkifQ.vry3sNOgr4PqRPi83pbCs6JAHUaUlJJApEq-LXIJubU'
        self.logger = None;
    
    # 暂时无法获取到cookie
    def login(self,username = 'root',password = ''):
        login_header = {
            "Content-Type":"application/x-www-form-urlencoded"
            #"Cookie":"Presto-UI-Token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyb290IiwiZXhwIjoxNjE5MDg2MTcyLCJhdWQiOiJwcmVzdG8tdWkifQ.II5qdon7c_nCQ3BBQhvv_dKQibtjYuMnDiIybhRpyzs"
        }
        login_url = "http://{}:{}{}".format(self.host,self.port,"/ui/api/login")
        form_data = "username={}&password={}&loginOptions=on&redirectPath=".format(username,password)
        response = requests.post(login_url,data = form_data,headers = login_header)
        #return Cookie

    def add_logging(self,log_file = None,log_level = logging.INFO):
        logger = logging.getLogger()
        logger.setLevel(log_level)
        if log_file is None:
            log_file = time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'
        log_handler = logging.FileHandler(log_file, mode='a')
        log_handler.setLevel(log_level) 

        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.info("connect to {}:{} user:{} catalog:{} schema:{}".format(self.host,self.port,self.user,self.catalog,self.schema))
        self.logger  = logger

    def __execute(self,sql):
        sql = sql.split(';')[0]
        response = requests.post(self.execute_url,data = sql,headers = self.headers)
        if response.ok:
            return Result(json.loads(response.text)['nextUri'])
        else:
            return response.text

    def execute(self,sql):
        return self.web_execute(self,sql)
        
    def web_execute(self,sql):
        if ';' in sql:
            sql = sql.split(';')[0]
        payload = {
            "query":sql,
            "sessionContext": {
                "catalog":self.catalog,
                "schema":self.schema
            }
        }
        payload_str = json.dumps(payload)
        #print(payload_str)
        response = requests.put(url = self.web_execute_url,data = payload_str,headers = self.headers)
        self.uuid = json.loads(response.text)[0]['uuid']
        return WebResult(sql,self.uuid,self,self.logger)

    # 多条执行，以;作为分割
    # 未测试
    def web_executes(self,sql):
        web_results = []
        sql_list = sql.split(';')
        for sql in sql_list:
            web_result = self.web_execute(sql)
            web_results.append(web_result)
        return web_results

    def web_execute_from_file(self,filename):
        with open(filename,'r') as file:
            web_results = self.web_executes(file.read())
        return web_results

    def get_all_query(self):
        response = requests.get(self.get_history_url,headers = self.headers)
        query_list = json.loads(response.text)
        return query_list

    def get_query(self,uuid):
        query_list = self.get_all_query()
        for query in query_list:
            if query['uuid'] == uuid:
                return query
        return None

if __name__ == "__main__":
    client = Client(host='192.168.40.152',port=18080,user='lk',catalog='clickhouse223',schema='tsg_galaxy_v3')
    client.add_logging(log_level=logging.DEBUG)


