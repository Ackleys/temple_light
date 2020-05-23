# 按摩椅，娃娃机，上门洗车，充电站，洗衣机，贩卖机等产品的后台程序
======================

:Date: 2017-08-11


数据库
-----------
.. code:: bash

    sudo apt-get install mysql-server
    sudo apt-get install mongodb


环境搭建
-----------

.. code:: bash
    
    sudo apt-get install python3.6
    sudo apt-get install python3-pip

    sudo apt-get install python3-mysql.connector

    sudo pip3 install -r requirements.txt

    cd street_app_server
    python3 manage.py shell
    >> db.create_all()

运行
--------------------

.. code:: bash
    
    cd street_app_server
    python3 manage.py runserver
    # Or run in shell
    cd street_app_server
    python3 manage.py shell