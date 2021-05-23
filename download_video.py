import shutil
import requests
import os

auth='Bearer XXXXXXXXXXXXXXXXX' # your token
start_time='10.05.2021 22:10'
stop_time='10.05.2021 22:11'
#start_time='14.05.2021 12:47'
#stop_time='14.05.2021 12:57'
url="https://cams.is74.ru/archive/cam964.m3u8?START_TIME="+start_time.replace(' ','%20')+"&STOP_TIME="+stop_time.replace(' ','%20')

r = requests.get(url, headers={'Authorization': auth})
file = open(start_time.replace(':','.')+'-'+stop_time.replace(':','.')+'.m3u8', "w")
file.write(r.text)
file.close()

lst_files = []
for line in r.iter_lines():
    line=str(line)
    if line[2]=='/':
        ts_url=line[2:].replace("'",'')
        lst_files.append(ts_url[1:])
        print(ts_url)
        if False:#можно добавить проверку того что файл существет, чтобы не скачивать по второму разу одно и то же
            continue
        r_ts=requests.get("https://cams.is74.ru"+ts_url, headers={'Authorization': auth},stream=True)
        try:
            os.makedirs(ts_url[1:]) #.replace('/','\\')
        except FileExistsError:
            None
        try:
            os.rmdir(ts_url[1:]) # .replace('/','\\')
        except NotADirectoryError:
            None
        with open(ts_url[1:], 'wb') as out_file: #.replace('/','\\')
            shutil.copyfileobj(r_ts.raw, out_file)
        del r_ts

files_str = ' '.join(lst_files)
save_path = 'archive/' + start_time + ' - ' + stop_time + '.ts'
os.system(f'cat {files_str} > "{save_path}"')
os.system(f'mv *.m3u8 archive/')

shutil.rmtree('archive/main')
import subprocess
outfile = save_path[:-2] + 'mp4'

subprocess.run(['ffmpeg', '-i', save_path, outfile])
os.remove(save_path)