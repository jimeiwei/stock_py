import stock_py
import stock_py_comm as comm
import time



#初始化接口
def stock_sys_init():
    #登陆系统
    global cfg_stock_match_list
    global cfg_stock_choose_list

    stock_py.stock_py_login_in()
    #获取全部股票信息
    stock_py.stock_py_all_stcok_info_get()
    #获取模式匹配股票信息
    cfg_stock_match_list = stock_py.stock_py_read_match_file()
    #获取自选股票信息
    cfg_stock_choose_list = stock_py.stock_py_read_self_choose_file()
    cfg_stock_match_list = [["太阳纸业"], ["看着要涨停"], [stock_py.STOCK_ACTION_TYPE_ADD], ["1"]]
    if cfg_stock_match_list.__len__() == 4:
        stock_py.stock_py_fun_match_notice(cfg_stock_match_list)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # thread_id = comm.stock_py_create_new_thread(stock_py.stock_py_fun_match_notice,
    #                                             (["sh000001"], ["ceshi"], [stock_py.STOCK_ACTION_TYPE_ADD], [1]))

    stock_sys_init()
    pass



