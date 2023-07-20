#!/bin/bash

file_path() {
  readlink -f ${1} | sed "s/$(echo ${1} | sed "sx./xxg")//g"
}

# fresh start
while getopts 'f' flag; do
  case "${flag}" in
    f)
      apt-get -qqy update
      apt-get -qqy install jq pv tar bzip2 wget sed cron grep readlink

      wget -nc -P /usr/local/bin https://github.com/Backblaze/B2_Command_Line_Tool/releases/latest/download/b2-linux
      [ -f /usr/local/bin/b2-linux ] && chmod +x /usr/local/bin/b2-linux
      [ -f /usr/local/bin/b2-linux ] && mv /usr/local/bin/b2-linux /usr/local/bin/b2
      [ -f /usr/local/bin/b2 ] && ln -fs /usr/local/bin/b2 /usr/bin/b2

      cron_command="cd $(file_path ${0}) && ${0}"
      grep "${cron_command}" /etc/crontab || echo "0 5 * * * root ${cron_command}" >> /etc/crontab

    ;;
  esac
done

dump_dir_path=archive_dump
bzipped_backup_file_path=backup_$(date +"%d-%m-%y").tar.bz2
backup_config_file=config.json

if [ ! -f ${backup_config_file} ]
then
    echo "no config file found, an example one was created for you in current directory: ${backup_config_file}"
    echo '{
  "buckets": [
    {
      "b2_app_key_id": "example",
      "b2_app_key": "example",
      "name": "example",
      "files": [
        {
          "system_path": "example",
          "bucket_path": "example"
        }
      ]
    }
  ]
}' > ${backup_config_file}
    exit 2
fi

# echoes the specified field from config json
# (property name)
config() {
  jq $1 ${backup_config_file} | sed 's/"//g'
}


for ((i = 0; i < $(jq '.buckets | length' ${backup_config_file}); i ++))
do
  bucket_app_key_id=$(config .buckets[${i}].b2_app_key_id)
  bucket_app_key=$(config .buckets[${i}].b2_app_key)
  bucket_name=$(config .buckets[${i}].name)

  b2 authorize-account ${bucket_app_key_id} ${bucket_app_key} 2>> errors.log

  for (( j = 0; j < $(jq '.buckets['${i}'].files | length' ${backup_config_file}); j++ )) 
  do
    system_path=$(config .buckets[${i}].files[${j}].system_path)
    bucket_path=$(config .buckets[${i}].files[${j}].bucket_path)

    mkdir -p ${dump_dir_path}$(file_path ${system_path})
    cp -r ${system_path} ${dump_dir_path}$(file_path ${system_path})

    tar cf - ${dump_dir_path} | pv -s $(du -sb ${dump_dir_path} | awk '{print $1}') | bzip2 -9 - > ${bzipped_backup_file_path} 2>> errors.log
    b2 upload-file ${bucket_name} ${bzipped_backup_file_path} $(echo ${bucket_path} | sed "s/%/$(date +'%d-%m-%y')/g").tar.bz2 >> success.log 2>> errors.log
    rm -rf ${dump_dir_path} ${bzipped_backup_file_path} 2>> errors.log
  done
done

