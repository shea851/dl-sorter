import dlsorter_properties
import logging
import os
import re
import shutil


# rarpartexp = "^.*\.part(?!1\.|01\.|001\.)[0-9]{1,3}.*$"
rarpartexp = "^.*\.(?:part(?!1\.|01\.|001\.)[0-9]{1,3}|subs|sample).*$"


#  Create directory if it does not already exist
#  directory = absolute path to directory to create
def create_directory(directory):
    if not os.path.exists(directory):
        logging.debug("Create directory: " + directory)
        os.makedirs(directory)


#  Delete directory and all contents
#  directory = absolute path to any existing directory
def delete_directory(directory):
    if os.path.exists(directory):
        logging.debug("Remove directory: " + directory)
        shutil.rmtree(directory, ignore_errors=True)


#  Recursively search directory for files with extension and build list to return
#  directory = absolute path to directory to start recursive search from
#  extension = file extension of what you want to find (".rar") or (".mkv")
#  outlist = return list of absolute path files
def search_for_files(directory, extension):
    outlist = []
    for root, dirs, files in os.walk(os.path.abspath(directory)):
        for f in files:
            if f.endswith(extension) and not os.path.islink(os.path.join(root, f)):
                abs_f = os.path.join(root, f)
                sz = os.path.getsize(abs_f)
                if extension == '.mkv' and sz >= dlsorter_properties.ossearchmkvminsz:
                    outlist.append(abs_f)
                    logging.info("Found: " + os.path.basename(abs_f))
                    logging.debug("Found: " + abs_f)
                elif extension == '.rar':
                    if not re.match(rarpartexp, abs_f):  # Match rars like: part1, part01, part001
                        outlist.append(abs_f)
                        logging.info("Found: " + os.path.basename(abs_f))
                        logging.debug("Found: " + abs_f)
    return outlist


#  Recursively search directory for directories that end with string
#  directory = absolute path to directory to start recursive search from
#  endswithstr = string you want to look for at end of directory name ("_tmp")
#  outlist = return list of absolute path directories
def search_for_folders(directory, endswithstr):
    outlist = []
    if os.path.isdir(directory) and directory not in dlsorter_properties.downloaddirs:
        for root, dirs, files in os.walk(os.path.abspath(directory)):
            for d in dirs:
                if d.endswith(endswithstr):
                    abs_d = os.path.join(root, d)
                    outlist.append(abs_d)
    return outlist


#  Copy file
#  infile = absolute path original file
#  destination = absolute path destination
def copy_file(infile, destination):
    if os.path.exists(destination):
        for d in dlsorter_properties.downloaddirs:
            if d in infile:
                logging.info("Copy file: " + os.path.basename(infile) + " -> " + destination.replace(d, ".."))
        logging.debug("Copy file: " + infile + " -> " + destination)
        shutil.copy2(infile, destination)


#  Move file
#  infile = absolute path original file
#  destination = absolute path destination
def move_file(infile, destination):
    if os.path.exists(destination):
        for d in dlsorter_properties.downloaddirs:
            if d in infile:
                logging.info("Move file: " + os.path.basename(infile) + " -> " + destination.replace(d, ".."))
        logging.debug("Move file: " + infile + " -> " + destination)
        shutil.move(infile, destination)


#  Rename file
#  infile = absolute path current file
#  newname = absolute path new file name
def rename_file(infile, newname):
    if not os.path.exists(newname):
        logging.info("Rename file: " + os.path.basename(infile) + " -> " + os.path.basename(newname))
        logging.debug("Rename file: " + infile + " -> " + newname)
        os.rename(infile, newname)


#  Create symlink
#  src = absolute path to source file
#  dst = absolute path to desired symlink destination file
def create_symlink(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        logging.debug("Create symlink: " + src + " -> " + dst)
        os.symlink(src, dst)


#  Delete symlink
#  inlink = absolute path to symlink
def delete_symlink(inlink):
    if os.path.islink(inlink):
        logging.debug("Delete symlink: " + inlink)
        os.unlink(inlink)