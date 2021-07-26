

## convert clickhouse's sql into openlookeng's sql

import json
def txt_to_json():
    with open("poc-ch.txt",'r') as file:
        content = file.readlines()
        i = 1
        all = {}
        for line in content:
            all['Q'+ str(i)] = line
            i += 1

    with open("poc-ch.json",'w') as file:
        content = json.dumps(all)
        file.write(content)


# 脱密
def change_sql(origin_sql):
    changed_sql = origin_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    #changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    #changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")
    changed_sql = changed_sql.replace("$secret1","$secret2")

    #changed_sql = changed_sql.replace("$secret1","$secret2")

    return changed_sql

def ch_to_ol():
    with open("./poc-ch.json","r") as file:
        content = file.read()
        all = json.loads(content)
    olsql = {}
    for k,v in all.items():
        olsql[k] = change_sql(v)

    with open("./auto-ol.json","w") as file:
        file.write(json.dumps(olsql))

ch_to_ol()