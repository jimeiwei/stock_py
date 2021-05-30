import time  # 引入time模块
import inspect
import threading

STOCK_COMM_RTN_OK = 1
STOCK_COMM_RTN_ERR = 0
STCOK_COMM_PREVIOUS_MONTH = 2
STCOK_COMM_NEXT_MONTH = 1

"""互斥锁"""
STOCK_COMM_MUTEX_LOCK = 1
STOCK_COMM_MUTEX_UNLOCK = 0



# 检查返回值
def comm_check_rc(rtn, excp_code):
    if rtn != excp_code:
        frame, filename, line_number, function_name, lines, index = inspect.stack()[1]

        print("finename:{}, \nlines:{}, \nline_number:{}\n ".\
              format(filename, lines, line_number))

        exit(0)


# 获取当前时间，返回字符串
def stcok_py_curr_time_get():
    currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return currtime.split()[0]


# 获取当前时间的前两个月的时间
def stcok_py_curr_time_before_day_get():
    current_day = stcok_py_curr_time_get()
    year = current_day.split("-")[0]
    month = current_day.split("-")[1]
    day = current_day.split("-")[2]
    if int(day) > 27:
        day = 27

    if int(month) <= 2:
        year = int(year) - 1
        month = int(month) + 12 - STCOK_COMM_PREVIOUS_MONTH
    else:
        month = int(month) - STCOK_COMM_PREVIOUS_MONTH

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
    thread_id.join()

if __name__ == '__main__':
    pass
