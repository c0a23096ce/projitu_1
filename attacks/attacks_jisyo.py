import crypt

#salt = '$1$ABCDEFGH$'
#target = '$1$ABCDEFGH$mf/3we5q6Fe8fWCKtwGKk1'
salt ='$6$O/zgIwlwUdB90Lqq'
target = '$6$O/zgIwlwUdB90Lqq$dI/43a6pMURBsp0UQ8FvxbXM1jTGxEASzJNVzL.zIDDs9wQapl4FY5qiW5gcIG1AQvx7/Zg2.dZz3Yh5rWCpN0'

f = open('a.txt', 'r')
dictpasswds = f.readlines()
f.close()

for dictpasswd in dictpasswds:
    passwd = dictpasswd.rstrip('\n')
    print(passwd)
    cpass = crypt.crypt(passwd, salt)
    if cpass == target:
        print('Yes + ' + cpass)
        break

