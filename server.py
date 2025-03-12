import os
import http.server
import uploadserver
import shutil

working_dir = 'working'
inputs_dir = os.path.join(working_dir, 'inputs')
outputs_dir = os.path.join(working_dir, 'outputs')

os.makedirs(working_dir, exist_ok=True)
os.makedirs(inputs_dir, exist_ok=True)
os.makedirs(outputs_dir, exist_ok=True)

def handle_uploads():  
  import subprocess
  result = subprocess.run(['python', 'pixelization.py', '--input', working_dir, '--output', outputs_dir])
  if result.returncode != 0:
    print('Error processing images')
    return
  else:
    print('Images processed')
  
  # debug
  # for file in os.listdir(unprocessed_dir):
  #  old_file = os.path.join(unprocessed_dir, file)
  #  new_file = os.path.join(outputs_dir, file)
  #  shutil.copy(old_file, new_file)
    
  for file in os.listdir(working_dir):
    old_file = os.path.join(working_dir, file)
    if not os.path.isfile(old_file):
      continue
    new_file = os.path.join(inputs_dir, file)
    os.rename(old_file, new_file)

class Args:
  port = 8000
  cgi = False
  allow_replace = False
  bind = None
  directory = working_dir
  theme = 'dark'
  server_certificate = None
  client_certificate = None
  basic_auth = None
  basic_auth_upload = None
uploadserver.args = Args()

old_receive_upload = uploadserver.receive_upload
def new_receive_upload(handler: http.server.BaseHTTPRequestHandler):
  status, message = old_receive_upload(handler)
  
  if status != http.HTTPStatus.BAD_REQUEST:
    handle_uploads()
  
  return status, message
uploadserver.receive_upload = new_receive_upload

uploadserver.serve_forever()