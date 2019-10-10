import subprocess as s
import os
import sys
from time import sleep
#import pysnooper

report = []
#{'date':'','time':'','device type':''  ,'device SN':'' ,'carwall build':'',  'build environment':''   ,'cpu type':''  ,'arch':''      ,'has carwall':'',    'whetstone':'',  'Dhrystone':''  ,'used memory':'',      'cached memory':''    ,'rootfs':''}


def findFirstDecimalNum(i_list): #gets list as parameter and returns the first decimal number in that list.
    for i in i_list:
        try:
            if '.' in i:
                return float(i)
        except:
            pass
    return 0


def general_info():
    print('General Info')
    #date
    proc = s.run(['ssh', 'sveta@192.168.5.56', "date '+%H:%M:%S'; date '+%d/%m/%y';"], stdout=s.PIPE)
    ###Decode the results if you want the newlines to be printed literally
    time, date = proc.stdout.decode('utf-8').split('\n')[0:2]
    report.append(date)
    print(date)

    #time
    report.append(time)
    print(time)

    #device type
    print('Device type')
    proc = s.run(["uname", "-n"], stdout=s.PIPE)
    report.append(proc.stdout.decode('utf-8'))

    #device SN
    print('Device SN')
    proc = s.run(["cat", "/proc/cpuinfo"], stdout=s.PIPE)
    output = proc.stdout.decode('utf-8')
    if 'Serial' in output:
            output = proc.stdout.decode('utf-8')
            report.append(output[output.index('Serial'):].split(':')[1])
    else:
            report.append('0')
    print('Finish generate general info')


def if_karamba_installed():
    #carwall build#
    print('if carwall')
    try:
        proc = s.run(['wb-agent', '--version'],stdout=s.PIPE)
        output = proc.stdout.decode('utf-8')
        if 'Karamba Security' in output:
            report.append(output.split('\n')[1])
        else:
            report.append('none')
    except:
        report.append('none')

    #has carwall
    try:
        f = open('/sbin/wb-agent', 'r')
        f.close()
        f = open('/sbin/wb-alarm', 'r')
        f.close()
        report.append('true')
    except:
        report.append('false')


def check_build_env():
    #build enviroment
    print("Check build env")
    proc = s.run(['cat', '/etc/issue'],stdout=s.PIPE)
    output = proc.stdout.decode('utf-8')
    if 'Yocto' in output:
        report.append('Yocto')
    elif 'QNX' in output:
        report.append('QNX')
    else:
        report.append('not found build env')


def cpu_type():
    #CPU type
    print ("CPU type")
    proc = s.run(["dmesg"], stdout=s.PIPE)
    output = proc.stdout.decode('utf-8').split('\n')
    report.append('***')
    for line in output:
        if 'CPU:' in line:
            report[-1] = line.split(':')[1]
            break
        else:
            report[-1] = "failed"


def arch_type():
    # arch
    proc = s.run(["uname", '-m'], stdout=s.PIPE)
    report.append(proc.stdout.decode('utf-8'))


def disable_internet():
    #disable internet
    print("Disable internet connection")
    proc = s.run(["ifconfig"], stdout=s.PIPE)
    output = proc.stdout.decode('utf-8').split('\n\n')
    i_list = []
    for connection in output:
        conn = connection.split(':')[0]
        if 'wlan' in conn or 'wifi' in conn or 'eth' in conn:
            i_list.append(conn[:conn.index(' ')])
            s.run(["ifconfig",i_list[-1], 'down'])

def run_unixbench():
    #whet and dhry stone
    print("Run UnixBench")
    whet = []
    dhry = []
    WHET_I = 5
    DHRY_I = 4
    try:
        os.chdir('/UnixBench')
        proc = s.run(['./Run', 'dhry', 'whets'], stdout=s.PIPE)
        output = proc.stdout.decode("utf-8")
        output = output.split(72*'-')[-1].split('\n')
        whet.append(findFirstDecimalNum(output[WHET_I].split(' ')))
        dhry.append(findFirstDecimalNum(output[DHRY_I].split(' ')))
        whet = str(sum(whet)/len(whet))#this and next line are ment to create average if loop is used
        dhry = str(sum(dhry)/len(dhry))
    except Exception as e:
        print(str(e))
        whet = 'no data'
        dhry = 'no data'
    report.append(whet)
    report.append(dhry)


def used_cached_memory():
    # used and cached
    print("Used memory")
    USED_INDDEX = 3
    CACHE_INDEX = -1
    used, cached = 0,0
    for i in range(3):
        proc = s.run(['free', '-w'], stdout=s.PIPE)
        output = proc.stdout.decode("utf-8")
        if 'total' in output:
            list = proc.stdout.decode("utf-8").split("\n")[1].split("    ")
            used += int(list[USED_INDDEX])
            cached += int(list[CACHE_INDEX])
        else:
            used, cached = 0,0
    report.append(str(used/(i+1)))
    report.append(str(cached/(i+1)))


def rootfs():
    #rootfs
    print("Rootfs")
    proc = s.run(['/usr/bin/du', '-sxk','/'], stdout=s.PIPE)
    report.append(proc.stdout.decode('utf-8').split('/')[0])


def enable_internet():
    #enable internet
    print("Enable internet")
    for connection in i_list:
        proc = s.run(["ifconfig", connection, 'up'])
    sleep(15)


def send_report():
    #to send report over ssh, and remote computer will append it to file
    print("Send report")
    with open('perf_report.txt', 'w', encoding='utf-8') as file:
        print('open file')
        for i in report:
            print(i)
            file.write(i)
        print(file)
    file_path = "/UnixBench/perf_report1.txt"
    server_path = "/home/sveta"
    os.system("scp "+file_path+" sveta@192.168.5.56:"+server_path)

    #r_cmd = "echo "+','.join(report).replace('\n', '')+" >> performanceReport.csv"
    #proc = s.run(['ssh', 'sveta@192.168.5.56', r_cmd], stdout=s.PIPE)
    #print(proc.stdout.decode())


def main():
    #print("ddd")
    general_info()
    if_karamba_installed()
    check_build_env()
    cpu_type()
    arch_type()
    disable_internet()
    run_unixbench()
    used_cached_memory()
    rootfs()
    enable_internet()
    send_report()


if __name__ == "__main__":
    main()
