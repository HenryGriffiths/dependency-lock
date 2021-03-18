import subprocess
import os
import json

org = ''
repos = ['']
basebranch = ''


def run(args, returnoutput = False):
    while True:
        try:
            sp = subprocess.run(args, text = True, check = True, capture_output = returnoutput)
            if returnoutput:
                print(sp.stdout)
            return sp.stdout
        except:
            while True:
                print('Running ' + ' '.join(args) + ' Failed.')
                result = input('(R)etry or (C)ontinue? : ')
                if result.lower() == 'r':
                    break
                elif result.lower() == 'c':
                    try:
                        return sp.stderr
                    except:
                        print('FAILED TO RETURN ERROR')
                        return

os.chdir('{}/{}'.format(os.getcwd(), 'repos'))
for repo in repos:
    if not os.path.exists('{}/{}'.format(os.getcwd(), org)):
        os.makedirs('{}/{}'.format(os.getcwd(), org))
    os.chdir('{}/{}'.format(os.getcwd(), org))
    run(['rm', '-rf', repo])
    run(['git', 'clone', 'https://github.com/{}/{}.git'.format(org, repo)])
    os.chdir('{}/{}'.format(os.getcwd(), repo))
    run(['git', 'checkout', basebranch])
    run(['git', 'pull'])
    run(['git', 'checkout', '-b', 'feat/dependencylock'])
    with open('package.json') as json_file:
        package = json.load(json_file)
    if os.path.exists('{}/{}'.format(os.getcwd(), 'package-lock.json')):
        insttype = 'npm'
        with open('package-lock.json') as json_file:
            packagelock = json.load(json_file)
        for deptype in ['dependencies', 'devDependencies']:
            for dep in package[deptype]:
                package[deptype][dep] = packagelock['dependencies'][dep]['version']
    elif os.path.exists('{}/{}'.format(os.getcwd(), 'yarn.lock')):
        insttype = 'yarn'
        with open('yarn.lock') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        for deptype in ['dependencies', 'devDependencies']:
            for dep in package[deptype]:
                # print('"{}@{}":'.format(dep, package['dependencies'][dep]))
                for i, lockline in enumerate(content):
                    if '{}@{}'.format(dep, package[deptype][dep]) in lockline:
                        package[deptype][dep] = content[i+1].replace('version', '').replace('"', '').strip()
    with open('package.json', 'w') as json_file:
        json.dump(package, json_file, indent=2)
    run(['rm', '-rf', 'package-lock.json'])
    run(['rm', '-rf', 'yarn.lock'])
    run([insttype, 'install'])
    run(['git', 'add', '.'])
    run(['git', 'commit', '-S', '-m', 'chore(deps): none: locked dependencies', '--no-verify'])
    run(['git', 'push', '--set-upstream', 'origin', 'feat/dependencylock'])
    # prnum = run(['gh', 'pr', 'create', '--title', 'chore(deps): none: locked dependencies', '--body', 'Created by HenryGriffiths/dependency-lock', '-H', 'develop', '-B', 'feat/dependencylock', '-a'], returnoutput = True)
    # prnum = prnum.split('https://github.com/')[1].split('/pull/')[1].strip()
    os.chdir('{}/../../'.format(os.getcwd()))
os.chdir('{}/../'.format(os.getcwd()))