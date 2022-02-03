#!/bin/bash


# fresh start
while getopts 'f' flag; do
  case "${flag}" in
    f) 
      apt-get -qqy update
      apt-get -qqy install jq

      wget -P /usr/local/bin https://github.com/Backblaze/B2_Command_Line_Tool/releases/latest/download/b2-linux
      mv /usr/local/b2-linux b2
      ln -s /usr/local/bin/b2 /usr/bin/b2
    ;;
  esac
done

dump_dir_path=${TMPDIR}dump
bzipped_backup_file_path=${TMPDIR}backup_$(date +"%d-%m-%y").tar.bz2
backup_config_file=backup_config.json

if [ ! -f ${backup_config_file} ]
then
    echo "no config file found, an example one should look like this:"
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
}'
    exit 2
fi

# echoes the specified field from config json
# (property name)
config() {
  jq $1 ${backup_config_file}
}


for ((i = 0; i < $(jq '.buckets | length' ${backup_config_file}); i ++))
do
  bucket_app_key_id=$(config .buckets[${i}].b2_app_key_id)
  bucket_app_key=$(config .buckets[${i}].b2_app_key)
  bucket_name=$(config .buckets[${i}].name)

  # b2 authorize-account ${bucket_app_key_id} ${bucket_app_key}

  for (( j = 0; j < $(jq '.buckets['${i}'].files | length' ${backup_config_file}); j++ )) 
  do
    system_path=$(config .buckets[${i}].files[${j}].system_path)
    bucket_path=$(config .buckets[${i}].files[${j}].bucket_path)

    mkdir -p ${dump_dir_path}
    cp -r ${system_path} ${dump_dir_path}/$(dirname ${system_path})
  done
done


tar cf - ${dump_dir_path} | pv -s $(du -sb ${dump_dir_path} | awk '{print $1}') | bzip2 -9 - > ${bzipped_backup_file_path}
# b2 upload-file ${bucket_name} ${bzipped_backup_file_path} ${bucket_path}

cat ${dump_dir_path} ${bzipped_backup_file_path}
rm -rf ${dump_dir_path} ${bzipped_backup_file_path}