#!/usr/bin/env python3
import time
import os
import subprocess
import signal


def run_offline_media_servers():
    run_servers_cmd = './run_servers ../settings_offline.yml'
    p1 = subprocess.Popen(run_servers_cmd, shell=True)


def start_maimahi_clients(num_clients):
    plist = []
    try:
        trace_dir = "/home/ubuntu/fcc_mahimahi_traces"
        # To test nowrway traces use: /home/ubuntu/norway_traces"
        files = os.listdir(trace_dir)
        for filename in files:
            # mahimahi_cmd = 'mm-delay 40 mm-link 12mbps ' + trace_dir + '/' + \
                            filename
            base_port = 9361
            plist = []
            for i in range(1, num_clients + 1):
                port = base_port + i
                #chrome_cmd = 'chromium-browser --headless --disable-gpu --remote-debugging-port=9222 ' + \
                #             'http://$MAHIMAHI_BASE:8080/player/?wsport=' + \
                #             str(port) + ' --user-data-dir=./' + str(port) + \
                #             '.profile'
                mahimahi_chrome_cmd = "mm-link 12mbps.trace {}/{} --meter-downlink -- \
                sh -c 'chromium-browser --headless --disable-gpu --remote-debugging-port=9222 \
                http://$MAHIMAHI_BASE/player/?wsport={} \
                --user-data-dir=./{}.profile'".format(trace_dir, filename, port, port)
                chrome_cmd_b = mahimahi_chrome_cmd.encode('utf-8')
                p = subprocess.Popen(mahimahi_cmd, shell=True,
                                     preexec_fn=os.setsid)
                plist.append(p)

            time.sleep(60*10)
            for p in plist:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)

            subprocess.check_call("killall chromium-browser", shell=True)
            subprocess.check_call("rm -rf ./*.profile", shell=True,
                                  executable='/bin/bash')
    except:
        pass
    finally:
        for p in plist:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)


def main():
    subprocess.check_call('sudo sysctl -w net.ipv4.ip_forward=1', shell=True)
    # run_media_servers()
    start_maimahi_clients(2)


if __name__ == '__main__':
    main()
