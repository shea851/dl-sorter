from datetime import timedelta
import dlsorter_os
import logging
import os
import re
import subprocess
import time


listrarexp = ".*:[0-9]{2}\ \ (.*)"


#  Extract archive into tmp folder
#  inlist = absolute path to archive (.rar) file and tmp dir
#  inlist format: ['/path/to/file.rar', '/path/to/file.rar_tmp']
def unrar(inlist):
    if not inlist:  # Only do stuff if necessary
        return
    for i in inlist:
        infile = i[0]  # ex: /path/to/file.rar
        extdir = i[1]  # ex: /path/to/file.rar/something_tmp
        dlsorter_os.delete_directory(extdir)  # Clean up existing directory
        dlsorter_os.create_directory(extdir)  # We need a place to put files we extract
        logcmd = ['/usr/bin/unrar', 'e', '"{}"'.format(infile), '"{}"'.format(extdir)]
        runcmd = ['/usr/bin/unrar', 'e', infile, extdir]
        logging.debug("Extract: [START] Command -> " + ' '.join(map(str,logcmd)))
        start = time.time()
        p = subprocess.Popen(runcmd, stdout=open(os.devnull, 'wb'), stderr=subprocess.PIPE)
        out, err = p.communicate()
        end = time.time()
        elapsed = str(timedelta(seconds=(end-start))).split(".")[0]
        if p.returncode == 0:
            logging.debug("Extract: [FINISH] Total time -> " + elapsed)
            logging.info("Extract: [" + elapsed + "] " + os.path.basename(infile) + " -> ../" + os.path.basename(extdir))
        else:
            logging.error(err.replace("\n", "  "))
            logging.error("Extract: [FAILURE]")


def list_rar_files(infile):
    # add debug logging??
    runcmd = ['/usr/bin/unrar', 'l', infile]
    p = subprocess.Popen(runcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    outlist = re.findall(listrarexp, out, re.MULTILINE)
    return outlist
