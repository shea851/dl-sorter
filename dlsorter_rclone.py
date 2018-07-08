from datetime import timedelta
import dlsorter_properties
import logging
import subprocess
import time


rclonebin = "/usr/sbin/rclone"


# Copy file(s) to rclone mount
# inlist = list of src and dst
def rclone_copy(inlist):
    for i in inlist:
        src = i[0]  # This is the basepath every time
        files = "{" + ','.join(map(str, i[1])) + "}"
        dst = i[2]
        logging.debug("Rclone copy: [details] src -> " + src)
        logging.debug("Rclone copy: [details] files -> " + files)
        logging.debug("Rclone copy: [details] dst -> " + dst)
        logcmd = [rclonebin,
                  'copy',
                  '"{}"'.format(src),
                  '"{}"'.format(dst),
                  '--copy-links',
                  '--max-depth', '0',
                  '--include', files,
                  '--stats', dlsorter_properties.rclonestatsinterval,
                  '-v']
        runcmd = [rclonebin,
                  'copy',
                  src,
                  dst,
                  '--copy-links',
                  '--max-depth', '0',
                  '--include', files,
                  '--stats', dlsorter_properties.rclonestatsinterval,
                  '-v']
        logging.debug("Rclone copy: [START] Command -> " + ' '.join(map(str, logcmd)))
        logging.info("Rclone copy: Files -> " + files)
        logging.info("Rclone copy: Destination -> " + dst)
        start = time.time()
        p = subprocess.Popen(runcmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            if "done" in line and dlsorter_properties.rclonestatslogging is True:
                logging.info(line.replace("\n", ""))
            elif "Copied" in line:
                logging.info(line.split("  : ")[1].replace("\n", ""))
        out, err = p.communicate()
        end = time.time()
        elapsed = str(timedelta(seconds=(end - start))).split(".")[0]
        if p.returncode == 0:
            logging.info("Rclone copy: [FINISH] Total time -> " + elapsed)
        else:
            logging.error(out)
            logging.error("Rclone copy: [FAILURE] -> QUITTING SCRIPT")
            quit()  # I think we want to exit here because if one fails, they all should..
