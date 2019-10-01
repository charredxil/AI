import sys
solutions_1 = [
    r'/^0$|^10[01]$/',
    r'/^[01]*$/',
    r'/0$/',
    r'/\b\w*[aeiou]\w*[aeiou]\w*\b/i',
    r'/^1[01]*0$|^0$/',
    r'/^[01]*110[01]*$/',
    r'/^.{2,4}$/s',
    r'/^\d{3} *-? *\d\d *-? *\d{4}$/',
    r'/^.*?d/m',
    r'/^1[01]*1$|^0[01]*0$|^0$|^1$/',
]
solutions_2 = [
    r'/\b[pck]\w*\b/i',
    r'/^.(..)*$/s',
    r'/^(0([01]{2})*|1([01]{2})*[01])$/',
    r'/^(1?0)*1*$/',
    r'/^[ox.]{64}$/i',
    r'/^[ox]*\.[ox]*$/i',
    r'/^((x+o*\.|\.)[.ox]*|[.ox]*(\.o*x+|\.))$/i',
    r'/^(a|[bc]*a?[bc]+|[bc]+a?[bc]*)$/',
    r'/^(a[bc]*a|[bc]+)+$/',
    r'/^(1[02]*1|2)(1[02]*1|[02]+)*$/'
]
solutions_3 = [
    r'/(.)\1{9}/s',
    r'/(\w)\w*\1/i',
    r'/(\w)+\1\w*/i',
    r'/\b(\w)+\w*\1\w*\b/i',
    r'/^(0|1)([01]*\1)?$/'
]
solutions_4 = [
    r'/\b(?=\w{6}\b).*?cat\w*/i',
    r'/^(0|1)[01]*(?<=\1)$/',
    r'/^(?=(0|1)*$)\1/',
    r'/\b([aeiou])\w*?(?!\1)[aeiou]\b/i',
    r'/^(?!.*011)[01]*$/'
]

solutions = solutions_1 + solutions_2 + solutions_3 + solutions_4
try:
    print(solutions[int(sys.argv[1])-31])
except:
    for ix, s in enumerate(solutions, start=31):
        print('{}.\t{}'.format(ix, s))
