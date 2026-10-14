import datetime
import os
import json

# TODO only pull updated repo (within 2 months)
def main():
    local_path = 'E:\\Backup\\github'

    local_folders = []
    tmp_list = os.listdir(local_path)
    for tmp in tmp_list:
        if os.path.isdir(local_path+'\\'+tmp):
            local_folders.append(tmp)
    print_log('local_folders: '+str(local_folders))

    remote_folders = []
    cmd = 'gh repo list --limit 999 --json name,updatedAt phoenixlam'
    json_str = os.popen(cmd).read()
    json_arr = json.loads(json_str)
    for repo in json_arr:
        remote_folders.append(repo['name'])
    print_log('remote_folders: '+str(remote_folders))

    diff_list = list(set(remote_folders) - set(local_folders))
    print_log('diff_list: '+str(diff_list))
    for repo in diff_list:
        cmd = 'gh repo clone phoenixlam/'+repo+' '+local_path+'\\'+repo
        print_log(cmd)
        os.system(cmd)

    for repo in remote_folders:
        if repo in local_folders:
            os.chdir(local_path+'\\'+repo)
            cmd = 'git pull origin'
            print_log(repo+': '+cmd)
            os.system(cmd)

def print_log(msg):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + msg)

main()
