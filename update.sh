#!/bin/bash
########################################################################
# File Name: update.sh
# Author: zioer
# mail: next4nextjob@gmail.com
# Created Time: 2022年01月10日 星期一 17时58分41秒
#
# 更新文件列表信息
#
########################################################################

source $HOME/.bashrc

wkdir=`dirname $0`
cd $wkdir

url_base="https://raw.githubusercontent.com/Awkee/china-ip-list/main"
iplist="ip.list"

# 更新ip目录下到IP段文件
fetch() {

    py_path="`which python3`"
    if [ "$py_path" = "" ]  ; then 
        echo "没找到python3环境，安装Python3.9"
        sudo apt install -y python3 python3-pip
    fi

    echo "安装Python3 依赖包:" && sudo python3 -m pip install -r ./requirements.txt

    echo "开始采集IP段数据:" && python3 ./fetch_ip.py
}

update() {
    echo "开始生成 ip.list 列表文件"
    echo > $iplist
    for fn in `ls ./ip/*.txt`
    do
        # echo "$url_base/$fn" >> $iplist
        echo "$fn" >> $iplist
    done
}

usage() {
    cat <<END
Usage:
    `basename $0` <init|fetch|update>

    fetch: 采集国内IP段数据(定期更新)
    update: 更新 ip.list 文件(主要第一次执行时使用，生成一次后再也不用更新)

    init: 第一次初始化执行
END
}

case "$1" in
    fetch|update)
        $1
    ;;
    init)
        fetch
        update
    ;;
    *)
        usage
    ;;
esac
