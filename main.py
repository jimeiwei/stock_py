import stock_py
import stock_py_comm as comm
import time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    thread_id = comm.stock_py_create_new_thread(stock_py.stock_py_fun_match_notice,
                                                ("sh000001", "ceshi", stock_py.STOCK_ACTION_TYPE_ADD, 1))

    while 1:
        pass


