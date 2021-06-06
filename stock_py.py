import stock_py_comm as comm
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


STOCK_LOW_PRICE_PERCENT_FLAG = 0.5
STOCK_LOW_PRICE_FLAG = 1
STOCK_NOT_LOW_PRICE_FLAG = 0

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
    rs = bs.query_all_stock(day=comm.stock_py_close_wrok_day_get())
    if rs.error_code == "0":
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
        comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, "[NOTCICE]: all stock info exported succeed")
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

    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, 'query_history_k_data_plus respond error_code:' + rs.error_code)
    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, 'query_history_k_data_plus respond  error_msg:' + rs.error_msg)

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
    dict_value_k = {"ingore_flag":0}
    value_k = 0
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      comm.stcok_py_curr_time_before_day_get(),day,
                                      "d", '2')
    comm.comm_check_rc(rs.error_code, "0")
    if rs.error_code == "0":
        for i in range(type):
            value_k = 0
            #day = rs.data[0 - 2*type + i + int( list(range(1, type+1))[-1] ) ][0]
            for j in list(range(0, type)):
                try:
                    value_k += float(rs.data[0 - 2*type + i + j][5])
                except IndexError:
                    dict_value_k["ingore_flag"] = 1
                    return dict_value_k

                #value_k += float(rs.data[0 - 2*type + i + j][5])
            dict_value_k[i] = round(value_k / type, 3)    #计算k线值，并保留三位小数

    return dict_value_k

#获取配置文件接口
def stock_py_read_match_file(filename="./cfg_file/config_match_stock.ini"):
    cfg_stock_match_list = []

    if not os.path.exists("cfg_file"):
        os.mkdir("cfg_file")

    if not os.path.exists(filename):
        fp = open(filename,"w")
        fp.close()

    if os.path.exists(filename):
        fd = open(filename, 'r')
        cfg_buff = fd.readlines()
        for i in range(cfg_buff.__len__()):
            if(":" not in cfg_buff[i]):
                continue
            else:
                stock_num = cfg_buff[i][cfg_buff[i].index(":")+1:].lstrip()
                if stock_num not in DICT_ALL_STOCK_INFO:
                    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,
                                       "{} is not a vaild stock name".format(str(stock_num)))
                else:
                    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,
                                       "stock {} searched".format(str(stock_num)))
                    cfg_stock_match_list.append(stock_num)
        fd.close()
        if cfg_stock_match_list.__len__() == 0:
            comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,
                               "[warning]:config stack is empty or no vaild stock_code")
    else:
        comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,"[warning]:file {} doesnt exists".format(filename))

    return cfg_stock_match_list

#获取配置文件接口
def stock_py_read_self_choose_file(filename="./cfg_file/config_self_choose_stock.ini"):
    choose_stock_list = []

    if not os.path.exists("cfg_file"):
        os.mkdir("cfg_file")
        fp = open("./cfg_file/config_self_choose_stock.ini", "w")
        fp.close()
        comm.comm_retrun()

    if os.path.exists(filename):
        fd = open(filename, 'r')
        choose_buff = fd.readlines()
        if(choose_buff.__len__() == 0):
            comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, "[NOTICE]：no self choose match")
            return choose_stock_list

        for i in range(choose_buff.__len__()):
            if (":" not in choose_buff[i]):
                continue
            else:
                stock_num = choose_buff[i][choose_buff[i].index(":") + 1:].lstrip()
                if stock_num not in DICT_ALL_STOCK_INFO :
                    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, "{} is not a vaild stock name".format(str(stock_num)))
                else:
                    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,
                                       "stock {} searched".format(str(stock_num)))
                    choose_stock_list.append(stock_num)

        fd.close()
        if choose_stock_list.__len__() == 0:
            comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, "[warning]:config stack is empty or no vaild stock_code")
    else:
        comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG, "[warning]:file {} doesnt exists".format(filename))

    return choose_stock_list

#分析主接口
def stock_py_fun_analysis_someone_stock(args):
    codes, match_types = args
    while(1):
        rc = comm.stock_py_mutex_try_to_lock(mutex_match)
        if not rc:
            for code, match_type in zip(codes, match_types):
                if not g_list_match_stock_buff[code]["is_stop"]:
                    print("code = {}\n".format(args[0]))
            else:
                break
        else:
            time.sleep(5)

#条件匹配接口
def stock_py_fun_match_notice(args):
    global g_match_fun_thread_id

    codes, reasons, action_codes, match_types = args
    while(1):
        rc = comm.stock_py_mutex_try_to_lock(mutex_match)
        if not rc:
            if (len(codes) == len(reasons) == len(action_codes) == len(match_types)) and len(codes) > 0:
                for code, reason, action_code, match_type in zip(codes, reasons, action_codes, match_types):
                    if code in g_list_match_stock_buff:
                        continue

                    g_match_stock_buff.match_type = match_type
                    g_match_stock_buff.code = code
                    g_match_stock_buff.reason = reason
                    g_match_stock_buff.days = time.strftime("%Y-%m-%d", time.localtime())

                    if action_code == STOCK_ACTION_TYPE_ADD:
                        g_list_match_stock_buff[code] = {}
                        g_list_match_stock_buff[code]["code"] = g_match_stock_buff.code
                        g_list_match_stock_buff[code]["match_type"] = g_match_stock_buff.match_type
                        g_list_match_stock_buff[code]["reason"] = g_match_stock_buff.reason
                        g_list_match_stock_buff[code]["days"] = g_match_stock_buff.days
                        g_list_match_stock_buff[code]["is_stop"] = 0
                        comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,"[notice]: code {} begin to analysis".format(code))

                    elif action_code == STOCK_ACTION_TYPE_REMOVE:
                        comm.stock_py_join_thread(g_list_match_stock_buff[code]["thread_id"])
                        time.sleep(10)

                        if code in g_list_match_stock_buff:
                            g_list_match_stock_buff.pop(code)
                    rc = comm.stock_py_mutex_release(mutex_match)
                    comm.comm_check_rc(rc, comm.STOCK_COMM_MUTEX_UNLOCK)
                break
        else:
            time.sleep(1)

    g_match_fun_thread_id = comm.stock_py_create_new_thread(stock_py_fun_analysis_someone_stock,
                                                            (codes, match_types))

"""计算金叉"""
def stock_py_golden_frok_get(ingore_second_board_flag=1, low_price_check=1):
    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,"begin stock_py_golden_frok_get")
    golden_fork = []
    most_close_work_day = comm.stock_py_close_wrok_day_get()
    into_anals_flag = 0

    for code in DICT_ALL_STOCK_INFO.keys():
        if code == '中证TMT产业主题指数' and into_anals_flag == 0:
            into_anals_flag = 1
            continue

        if into_anals_flag:
            #创业板
            if("sz.300" in DICT_ALL_STOCK_INFO[code]['code'] and ingore_second_board_flag):
                continue

            k_data_5 = stock_py_data_mov_k_data_get(DICT_ALL_STOCK_INFO[code]['code'], most_close_work_day, STOCK_MOV_K_TYPE_5)
            k_data_10 = stock_py_data_mov_k_data_get(DICT_ALL_STOCK_INFO[code]['code'], most_close_work_day, STOCK_MOV_K_TYPE_10)

            if (k_data_5["ingore_flag"] or k_data_10["ingore_flag"]):
                continue
            if low_price_check:
                if( not stock_py_most_low_price_check(DICT_ALL_STOCK_INFO[code]['code'] ,k_data_5[4])):
                    continue


            #符合以下几个条件
            #1. 5日均线和10日均线都属于向上趋势
            #2. 5日均线超过10日均线

            value_5_0 = k_data_5[0]
            value_5_1 = k_data_5[1]
            value_5_2 = k_data_5[2]
            value_5_3 = k_data_5[3]
            value_5_4 = k_data_5[4]
            value_10_0 = k_data_10[0]
            value_10_1 = k_data_10[1]
            value_10_2 = k_data_10[2]
            value_10_3 = k_data_10[3]
            value_10_4 = k_data_10[4]

            if (value_5_4 > value_10_4) and (value_5_3 > value_10_3) and (value_5_2 > value_10_2) and ( (value_5_1 < value_10_1) or (value_5_0 < value_10_0) ):
                if (value_5_4 - value_5_3 > 0) and (value_5_3 - value_5_2 > 0) and (value_10_4 - value_10_3 > 0) and (value_10_3 - value_10_2 > 0):
                    print(code)
                    golden_fork.append(code)
    #写入记录
    if golden_fork.__len__():
        comm.comm_write_to_file(comm.STOCK_RESULT_FILE_PATH, "code select as follows:\n")
        for code in golden_fork:
             comm.comm_write_to_file(comm.STOCK_RESULT_FILE_PATH, "code_name:{}\n".format(code))

    comm.stock_py_dlog(comm.STOCK_COMM_LOG_LEVEL_LOG,"finish stock_py_golden_frok_get")
    print("finish stock_py_golden_frok_get")

#判断价格是否是近期低价,判定方法是，最近一个工作日的收盘价与最近40个交易日的收盘价去比，如果低价总和占40天的一半以上，则认为是满足条件
def stock_py_most_low_price_check(code, price, end_day=comm.stock_py_close_wrok_day_get()):
    low_cnt = 1
    per_cent = 0
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      comm.stcok_py_curr_time_before_day_get(), end_day,
                                      "d", '2')
    comm.comm_check_rc(rs.error_code, "0")

    for i in rs.data:
        if float(i[5]) < price:
            low_cnt += 1

    if low_cnt > 0:
        per_cent = low_cnt / rs.data.__len__()

        if per_cent < STOCK_LOW_PRICE_PERCENT_FLAG:
            return STOCK_LOW_PRICE_FLAG

    return STOCK_NOT_LOW_PRICE_FLAG
















if __name__ == '__main__':
    pass
