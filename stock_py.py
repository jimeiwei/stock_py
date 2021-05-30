import stock_py_comm as comm
import numpy as np
import baostock as bs
import pandas as pd
import os
import threading
import time

"""声明"""
"""类"""
class match_stcok_buff:
    code = "code"
    reason = "reason"
    match_type = 0
    days = 0



"""全局变量"""
DICT_ALL_STOCK_INFO = {}
g_match_stock_buff = match_stcok_buff
g_list_match_stock_buff = {}

"""锁"""
mutex_match = threading.Lock()
mutex_choose = threading.Lock()

"""移动平行线级别"""
STOCK_MOV_K_TYPE_5 = 5
STOCK_MOV_K_TYPE_10 = 10
STOCK_MOV_K_TYPE_20 = 20
STOCK_MOV_K_TYPE_30 = 30
STOCK_MOV_K_TYPE_60 = 60
STOCK_MOV_K_TYPE_120 = 120



"""action type"""
STOCK_ACTION_TYPE_ADD = 0
STOCK_ACTION_TYPE_REMOVE = 1

# 获取登录状态
def stock_py_login_in():
    lg = bs.login()
    comm.comm_check_rc(lg.error_code, "0")



# 获取登录状态
def stock_py_log_out():
    lg = bs.logout()
    comm.comm_check_rc(lg.error_code, "0")



# 获取所有股票的信息
def stock_py_all_stcok_info_get():
    stock_py_login_in()
    rs = bs.query_all_stock()
    if rs.error_code != 0:
        for i in range(len(rs.data)):
            DICT_ALL_STOCK_INFO[rs.data[i][2]] = {}
            DICT_ALL_STOCK_INFO[rs.data[i][2]]["code"] = rs.data[i][0]
            DICT_ALL_STOCK_INFO[rs.data[i][2]]["tradeStatus"] = rs.data[i][1]
            DICT_ALL_STOCK_INFO[rs.data[i][2]]["code_name"] = rs.data[i][2]
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)

        #### 结果集输出到csv文件 ####
        result.to_csv("./cfg_file/all_stock.csv", encoding="gbk", index=False)
        print("[NOTCICE]: all stock info exported succeed")
    return comm.STOCK_COMM_RTN_OK


# 获取历史k线记录
# code 代码编号
# frequency：数据类型，默认为d，日k线；d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据，不区分大小写
# adjustflag：复权类型，默认不复权：3；1：后复权；2：前复权
def stock_py_data_history_k_data_get(code,
                                     frequency="d",
                                     start_day=comm.stcok_py_curr_time_before_day_get(),
                                     end_day=comm.stcok_py_curr_time_get(),
                                     adjustflag="2"):
    stock_py_login_in()
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=start_day, end_date=end_day,
                                      frequency=frequency, adjustflag=adjustflag)
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    return rs


#获取某只股票特定时间的交易记录
def stock_py_data_history_curr_day_data_get(code,
                                            frequency="d",
                                            time=comm.stcok_py_curr_time_get(),
                                            adjustflag="2"):
    stock_py_login_in()
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=time, end_date=time,
                                      frequency=frequency, adjustflag=adjustflag)
    comm.comm_check_rc(rs.error_code, "0")

    return rs

# 获取k线
def stock_py_data_mov_k_data_get(code, day, type=STOCK_MOV_K_TYPE_5):
    stock_py_login_in()
    dict_value_k = {}
    value_k = 0
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      day, comm.stcok_py_someone_time_next_month_get(day,type),
                                      "d", '2')
    comm.comm_check_rc(rs.error_code, "0")
    if rs.error_code == "0":
        for i in range(type):
            value_k = 0
            dict_value_k[i] = 0
            for j in range(type):
                value_k += float(rs.data[i+j][5])
            dict_value_k[i] = round(value_k / STOCK_MOV_K_TYPE_5, 3)    #计算k线值，并保留三位小数

    return dict_value_k

#获取配置文件接口
def stock_py_read_cfg_file(filename="./cfg_file/config_stock.ini"):
    cfg_stock_list = []

    if not os.path.exists("cfg_file"):
        os.mkdir("cfg_file")
        fp = open("./cfg_file/config_stock.ini","w")
        fp.close()

        fp = open("./cfg_file/config_self_choose_stock.ini", "w")
        fp.close()

    if os.path.exists(filename):
        cfg_buff = open(filename, 'r').readlines()
        for i in range(cfg_buff.__len__()):
            if(":" not in cfg_buff[i]):
                continue
            else:
                stock_num = cfg_buff[i][cfg_buff[i].index(":")+1:]
                cfg_stock_list.append(stock_num)

        if cfg_stock_list.__len__() == 0:
            print("[warning]:config stack is empty or no vaild stock_code")
    else:
        print("[warning]:file {} doesnt exists".format(filename))

    return cfg_stock_list


def stock_py_read_match_file():
    pass

def stock_py_read_self_choose_file():
    pass

#分析主接口
def stock_py_fun_analysis_someone_stock(args):
    code, match_type = args
    while(1):
        rc = comm.stock_py_mutex_try_to_lock(mutex_match)
        if not rc:
            if not g_list_match_stock_buff[code]["is_stop"]:
                print("code = {}\n".format(args[0]))

            else:
                break
        else:
            time.sleep(5)

#条件匹配接口
def stock_py_fun_match_notice(args):
    code, reason, action_code, match_type = args
    while(1):
        rc = comm.stock_py_mutex_try_to_lock(mutex_match)
        if not rc:
            if code in g_list_match_stock_buff:

                rc = comm.stock_py_mutex_release(mutex_match)
                comm.comm_check_rc(rc, comm.STOCK_COMM_MUTEX_UNLOCK)

                continue

            g_match_stock_buff.match_type = match_type
            g_match_stock_buff.code = code
            g_match_stock_buff.reason = reason
            g_match_stock_buff.days = time.strftime("%Y-%m-%d", time.localtime())

            if action_code == STOCK_ACTION_TYPE_ADD:
                g_list_match_stock_buff[code] = {}

                thread_id = comm.stock_py_create_new_thread(stock_py_fun_analysis_someone_stock,
                                                            (code, match_type))

                g_list_match_stock_buff[code]["code"] = g_match_stock_buff.code
                g_list_match_stock_buff[code]["match_type"] = g_match_stock_buff.match_type
                g_list_match_stock_buff[code]["reason"] = g_match_stock_buff.reason
                g_list_match_stock_buff[code]["days"] = g_match_stock_buff.days
                g_list_match_stock_buff[code]["thread_id"] = thread_id
                g_list_match_stock_buff[code]["is_stop"] = 0
                print("[notice]: code {} begin to analysis".format(code))
            elif action_code == STOCK_ACTION_TYPE_REMOVE:
                comm.stock_py_join_thread(g_list_match_stock_buff[code]["thread_id"])
                time.sleep(10)

                if code in g_list_match_stock_buff:
                    g_list_match_stock_buff.pop(code)


            rc = comm.stock_py_mutex_release(mutex_match)
            comm.comm_check_rc(rc, comm.STOCK_COMM_MUTEX_UNLOCK)
        else:
            time.sleep(1)





if __name__ == '__main__':
    pass
