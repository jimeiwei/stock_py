import stock_py_comm as comm
import numpy as np
import baostock as bs
import pandas as pd

DICT_ALL_STOCK_INFO = {}

#移动平行线级别
STOCK_MOV_K_TYPE_5 = 5
STOCK_MOV_K_TYPE_10 = 10
STOCK_MOV_K_TYPE_20 = 20
STOCK_MOV_K_TYPE_30 = 30
STOCK_MOV_K_TYPE_60 = 60
STOCK_MOV_K_TYPE_120 = 120


# 获取登录状态
def stock_py_login_in():
    lg = bs.login()


# 获取登录状态
def stock_py_log_out():
    lg = bs.logout()


# 检查返回值
def comm_check_rc(rtn, excp_code):
    if rtn != excp_code:
        exit(0)


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
        result.to_csv("all_stock.csv", encoding="gbk", index=False)

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
    comm_check_rc(rs.error_code, "0")
    if rs.error_code == "0":
        for i in range(type):
            value_k = 0
            dict_value_k[i] = 0
            for j in range(type):
                value_k += float(rs.data[i+j][5])
            dict_value_k[i] = round(value_k / STOCK_MOV_K_TYPE_5, 3)    #计算k线值，并保留三位小数

    return dict_value_k

if __name__ == '__main__':
    pass
