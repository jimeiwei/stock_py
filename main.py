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

    list_steam_stcok_infos_20d = []
    list_steam_stcok_infos_10d = []

    list_steam_stcok_infos_20d = stock_py.stock_py_steam_num_get(stock_py.STOCK_MOV_K_TYPE_20, stock_py.STOCK_STREAM_PRICE_PERCENT_D20)
    print('-----------------------STOCK_MOV_K_TYPE_20-----------------------------')
    list_steam_stcok_infos_10d = stock_py.stock_py_steam_num_get(stock_py.STOCK_MOV_K_TYPE_10, stock_py.STOCK_STREAM_PRICE_PERCENT_D10)
    print('-----------------------STOCK_MOV_K_TYPE_10&20-----------------------------')


    for i in [stock_10d[0] for stock_10d in list_steam_stcok_infos_10d]:
        if i not in [stock_20d[0] for stock_20d in list_steam_stcok_infos_20d]:
            print("code:{}, percent:{}".format(i, list_steam_stcok_infos_10d[list_steam_stcok_infos_10d.index(i)][1]))
