
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

ch_test(){
    collect_use_info
    echo "running ClickHouse test"
    python ./src/run.py ch $(pwd)
}

ol_test(){
    collect_use_info
    echo "running OpenLookeng test"
    python ./src/run.py ol $(pwd)
}

clear_log() {
    rm -rf ./log/*
    rm -rf ./src/__pycache__
}

start() {
    clear_log
    collect_info
    for i in {1,2,3}
    do
        ch_test
        ol_test
    done
    echo "finish poc test"
    tar -zcvf log.tgz ./log
}

start