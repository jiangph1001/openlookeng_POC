
pip_install(){
    pip install ./whl/clickhouse_driver-0.1.2-cp27-cp27mu-manylinux1_x86_64.whl >> ./log/install.log  2>&1
    if [ "$?" == 0 ]
    then 
        echo "install clickhouse_driver success"
    else
        echo "install clickhouse_driver error"
    fi
    pip install ./whl/requests_toolbelt-0.9.1-py2.py3-none-any.whl >> ./log/install.log  2>&1
    if [ "$?" == 0 ]
    then 
        echo "install requests_toolbelt success"
    else
        echo "install requests_toolbelt error"
    fi
}
docker_install(){
    #docker import poc.tar poc_jph:latest
    docker load < poc.tar 
    if [ "$?" == 0 ]
    then 
        echo "install success"
    else
        echo "install error"
    fi
    #docker run -d -v $(pwd):/usr/src/app --name poc poc_jph:latest
}

docker_install