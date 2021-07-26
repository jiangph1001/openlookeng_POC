#!/bin/bash
systeminfologfile="./log/systeminfo.log"
runtimelogfile="./log/runtime.log"
#alias python="docker run -it --rm poc_jph python"
collect_info(){
    echo co
    echo "--------" >> $systeminfologfile
    echo "CPU INFO" >> $systeminfologfile
    echo "--------" >> $systeminfologfile
    lscpu >> $systeminfologfile 2>&1
    echo "--------" >> $systeminfologfile
    echo "MEM INFO" >> $systeminfologfile
    echo "--------" >> $systeminfologfile
    cat /proc/meminfo >> $systeminfologfile 2>&1
    echo "--------" >> $systeminfologfile
    echo "LINUX INFO" >> $systeminfologfile
    echo "--------" >> $systeminfologfile
    uname -a >> $systeminfologfile 2>&1
}

collect_use_info(){
    echo 1 > /proc/sys/vm/drop_caches 
    echo "--------" >> $runtimelogfile
    echo "MEM USE" >> $runtimelogfile
    echo "--------" >> $runtimelogfile
    free -g >> $runtimelogfile 2>&1
    echo "--------" >> $runtimelogfile
    echo "CPU USE" >> $runtimelogfile
    echo "--------" >> $runtimelogfile
    mpstat >> $runtimelogfile 2>&1
}

ch_test_docker(){
    collect_use_info
    echo "running ClickHouse test" 
    docker exec -it poc python ./src/run.py ch /usr/src/app/
    #docker run --rm -v $(pwd):/usr/src/app --name poc poc_jph:latest python ./src/run.py ch /usr/src/app/

}

ol_test_docker(){
    collect_use_info
    echo "running OpenLookeng test" 
    docker exec -it poc python ./src/run.py ol /usr/src/app/
    #docker run --rm -v $(pwd):/usr/src/app --name poc poc_jph:latest ./src/run.py ol /usr/src/app/
}

ol_expain_docker(){
    collect_use_info
    echo "running Explaining test" 
    docker exec -it poc python ./src/run.py explain /usr/src/app/
}


clear_log() {
    rm -rf ./log/*
    rm -rf ./src/__pycache__
}

docker_start() {
    docker-compose up -d
    clear_log
    collect_info
    for i in {1,2,3}
    do
        ch_test_docker
        ol_test_docker
    done
    tar -zcvf log.tgz ./log
    docker-compose down
    echo "finish poc test"
}

docker_export() {
    docker save -o ./poc.tar poc_jph:latest
}

temp_test() {
    docker-compose up -d
    docker exec -it poc python ./src/run.py ch /usr/src/app/
    docker exec -it poc python ./src/run.py ol /usr/src/app/
    docker-compose down
}


explain_start() {
    docker-compose up -d
    clear_log
    collect_info
    for i in {1,2}
    do
        ol_expain_docker
    done
    tar -zcvf log.tgz ./log
    docker-compose down
    echo FINISH
}

docker_start