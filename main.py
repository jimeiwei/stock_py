import stock_py
import stock_py_comm as comm
import time



#初始化接口
def stock_sys_init():
    #登陆系统
    global cfg_stock_match_list
    global cfg_stock_choose_list

    comm.comm_remove_log_file()
    comm.comm_create_result_file()
    stock_py.stock_py_login_in()
    #获取全部股票信息
    stock_py.stock_py_all_stcok_info_get()
    #获取模式匹配股票信息
    cfg_stock_match_list = stock_py.stock_py_read_match_file()
    #获取自选股票信息
    cfg_stock_choose_list = stock_py.stock_py_read_self_choose_file()


if __name__ == '__main__':
    stock_sys_init()
    stock_py.stock_py_steam_num_get(stock_py.STOCK_MOV_K_TYPE_20)

