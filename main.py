import stock_py
import stock_py_comm as comm
import numpy as np
import baostock as bs
import pandas as pd


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    day = comm.stcok_py_curr_time_before_day_get()
    stock_py.stock_py_data_mov_k_data_get("sh.600406", day, stock_py.STOCK_MOV_K_TYPE_10)