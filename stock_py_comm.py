import time  # 引入time模块
import inspect
import threading
import os
import datetime
from pandas.tseries.offsets import BDay


STOCK_COMM_RTN_OK = 1
STOCK_COMM_RTN_ERR = 0
STCOK_COMM_PREVIOUS_MONTH = 2
STCOK_COMM_NEXT_MONTH = 1

"""互斥锁"""
STOCK_COMM_MUTEX_LOCK = 1
STOCK_COMM_MUTEX_UNLOCK = 0

"""记录登记"""
STOCK_COMM_LOG_LEVEL_DEBUG = 0
STOCK_COMM_LOG_LEVEL_LOG   = 1
STOCK_COMM_LOG_LEVEL_ERR   = 2

STOCK_LOG_FILE_PATH = "./cfg_file/stock_py_{}.log".format( time.strftime("%Y-%m-%d", time.localtime()) +  time.strftime("%H", time.localtime()))
STOCK_RESULT_FILE_PATH = "./cfg_file/result_{}.log".format( time.strftime("%Y-%m-%d", time.localtime()))


#初始化log文件
def comm_remove_log_file():
    if os.path.exists(STOCK_LOG_FILE_PATH):
        os.remove(STOCK_LOG_FILE_PATH)



def comm_create_result_file():
    if not os.path.exists(STOCK_RESULT_FILE_PATH):
        fp = open(STOCK_RESULT_FILE_PATH, "w")
        fp.close()
    else:
        os.remove(STOCK_RESULT_FILE_PATH)
        fp = open(STOCK_RESULT_FILE_PATH, "w")
        fp.close()


#写入文件
def comm_write_to_file(pathname, content):
    if not os.path.exists(pathname):
        fp = open(pathname, "w")
        fp.close()

    fd = open(pathname, "a")
    fd.write(content + "\n")
    fd.close()





# 检查返回值
def comm_check_rc(rtn, excp_code):
    if rtn != excp_code:
        frame, filename, line_number, function_name, lines, index = inspect.stack()[1]
        stock_py_dlog(STOCK_COMM_LOG_LEVEL_ERR, ("finename:{}, lines:{}, line_number:{}\n ".format(filename, lines, line_number)))

        print("finename:{}, \nlines:{}, \nline_number:{}\n ".\
              format(filename, lines, line_number))

        exit(0)

def comm_retrun():
    frame, filename, line_number, function_name, lines, index = inspect.stack()[1]
    stock_py_dlog(STOCK_COMM_LOG_LEVEL_LOG,
                  ("finename:{}, \nlines:{}, \nline_number:{}\n ".format(filename, lines, line_number)))

    print("finename:{}, \nlines:{}, \nline_number:{}\n ". \
          format(filename, lines, line_number))

    exit(0)

# 获取当前时间，返回字符串
def stcok_py_curr_time_get():
    currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return currtime.split()[0]



# 获取当前时间的前两个月的时间
def stcok_py_curr_time_before_day_get(month_set=2):
    current_day = stcok_py_curr_time_get()
    year = current_day.split("-")[0]
    month = current_day.split("-")[1]
    day = current_day.split("-")[2]
    if int(day) > 27:
        day = 27

    if int(month) <= month_set:
        year = int(year) - 1
        month = int(month) + 12 - month_set
    else:
        month = int(month) - month_set

    if (len(str(month)) < 2):
        month = '0' + str(month)

    if (len(str(day)) < 2):
        month = '0' + str(day)

    return str(year) + "-" + str(month) + "-" + str(day)


# 获取当前时间的后n个月的时间
def stcok_py_curr_time_next_month_get(type):
    current_day = stcok_py_curr_time_get()
    year = current_day.split("-")[0]
    month = current_day.split("-")[1]
    day = current_day.split("-")[2]

    month_type = int(type / 30 + 1)

    if int(day) > 27:
        day = 27

    if int(month) > 10:
        year = int(year) - 1
        month = int(month) + month_type - 12
    else:
        month = int(month) - month_type

    if (len(str(month)) < 2):
        month = '0' + str(month)

    if (len(str(day)) < 2):
        month = '0' + str(day)

    return str(year) + "-" + str(month) + "-" + str(day)


# 获取某一日期后几个月的日期
def stcok_py_someone_time_next_month_get(day, type):
    if not isinstance(day, str) or len(day.split("-")) != 3:
        exit(0)
    year = day.split("-")[0]
    month = day.split("-")[1]
    day = day.split("-")[2]

    month_type = int(type / 30 + 1)

    if int(day) > 27:
        day = 27

    if int(month) > 10:
        year = int(year) - 1
        month = int(month) + month_type - 12
    else:
        month = int(month) + month_type

    if (len(str(month)) < 2):
        month = '0' + str(month)

    if (len(str(day)) < 2):
        month = '0' + str(day)

    return str(year) + "-" + str(month) + "-" + str(day)


#尝试获取互斥锁，锁可以获取返回0，已锁返回1
def stock_py_mutex_try_to_lock(lock):
    rc = lock.acquire(False)
    if rc:
        return STOCK_COMM_MUTEX_UNLOCK
    else:
        #print("[warning]:mutex {} already locked".format(str(lock)))
        return STOCK_COMM_MUTEX_LOCK


#互斥锁加锁，成功返回1，失败返回0
def stock_py_mutex_lock(lock):
    rc = lock.acquire()

    if rc:
        return STOCK_COMM_MUTEX_LOCK
    else:
        return STOCK_COMM_MUTEX_UNLOCK

# 互斥锁释放锁，成功返回0，失败返回1
def stock_py_mutex_release(lock):
    rc = lock.release()

    if rc:
        return STOCK_COMM_MUTEX_LOCK
    else:
        return STOCK_COMM_MUTEX_UNLOCK

#create new thread
def stock_py_create_new_thread(fun, args):
    thread_py = threading.Thread(target=fun, args=(args,))
    thread_py.start()

    return thread_py


#回收线程
def stock_py_join_thread(thread_id):
    pass





#记录日志
def stock_py_dlog(level, content):
    frame, filename, line_number, function_name, lines, index = inspect.stack()[1]
    if level == STOCK_COMM_LOG_LEVEL_DEBUG:
        print(content)
    elif level == STOCK_COMM_LOG_LEVEL_LOG:
        if not os.path.exists(STOCK_LOG_FILE_PATH):
            fp = open(STOCK_LOG_FILE_PATH, "w")
            fp.close()

        fd = open(STOCK_LOG_FILE_PATH,"a")
        fd.write("time:{}, level:{}, filename:{}, line_number:{}, function_name:{}, content:{}\n".
                format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level,filename, line_number, function_name, content))
        fd.close()
    elif level == STOCK_COMM_LOG_LEVEL_ERR:
        #记录日志并退出
        if not os.path.exists(STOCK_LOG_FILE_PATH):
            fp = open(STOCK_LOG_FILE_PATH, "w")
            fp.close()

        fd = open(STOCK_LOG_FILE_PATH,"a")
        fd.write("time:{}, level:{}, filename:{}, line_number:{}, function_name:{}, content:{}\n".
                format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level,filename, line_number, function_name, content))
        fd.close()
        comm_retrun()

#确定今天是否是周六周日
def stock_py_weekday_sure():
    week_day = datetime.date.today().weekday()

    if week_day > 4:
        return 0
    else:
        return 1


def stock_py_close_stream_days_get():
    today = stcok_py_curr_time_get()
    day = today.split('-')[0] + '-' + today.split('-')[1] + '-'
    days = [day + str(i) for i in range(1,28)]

    return days


#最近工作时间获取
def stock_py_close_wrok_day_get():
    work_day_flag = stock_py_weekday_sure()
    day = stcok_py_curr_time_get()
    if work_day_flag:
        return day
    else:
        #非工作日，datetime.date.today().weekday() 5和6
        lastBusDay = datetime.datetime.today()
        shift = datetime.timedelta(max(1, (lastBusDay.weekday() + 6) % 7 - 3))
        lastBusDay = lastBusDay - shift

        return str(lastBusDay).split()[0]


if __name__ == '__main__':
    pass
