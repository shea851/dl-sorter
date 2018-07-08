import dlsorter_os
import dlsorter_properties
import logging
import os
import re


moviesexp = "^(?!.*S[0-9]{2}E[0-9]{2,3}).*(?:19|20)[0-9]{2}.*[HhXx]264.*$"
showsexp = "^(.*?).(?:|(?:19|20)[0-9]{2}.)[sS]([0-9][0-9])[eE][0-9][0-9].*$"


#  Determine if movie by checking parent folder name
#  infilename = absolute path to file (trimmed to base parent folder name)
#  outtype = return type
def determine_type_by_parent_folder_name(inpath, logbool):
    outtype = ""
    baseparentfoldername = os.path.basename(os.path.dirname(inpath))
    if re.match(moviesexp, baseparentfoldername):
        if logbool:
            logging.info("Regex: [MATCH] Movie -> " + baseparentfoldername)
        outtype = "movie"
    else:
        if logbool:
            logging.debug("Regex: [FAILURE] -> " + baseparentfoldername)
    return outtype


#  Determine if show or movie by checking base name
#  inpath = absolute path to file/folder (trimmed to base name)
#  outtype = return type
def determine_type_by_base_name(inpath, logbool):
    outtype = ""
    basename = os.path.basename(inpath)
    if re.match(showsexp, basename):
        if logbool:
            logging.info("Regex: [MATCH] Show -> " + basename)
        outtype = "show"
    elif re.match(moviesexp, basename):
        if logbool:
            logging.info("Regex: [MATCH] Movie -> " + basename)
        outtype = "movie"
    else:
        if logbool:
            logging.debug("Regex: [FAILURE] -> " + basename)
    return outtype


#  Retrieve show name and season
#  inpath = any path to directory or file (it will be trimmed to base name)
#  Return outlist
def get_show_info(inpath):
    outlist = []
    basename = os.path.basename(inpath)
    m = re.match(showsexp, basename)  # No need to verify this match
    outlist.append(m.group(1))
    outlist.append(m.group(2))
    return outlist


#  Retrieve existing show folder if it exists
#  name = regex matched name with .'s removed
#  Return show folder name
def get_existing_show_folder_name(inname):
    outname = ""
    remotedir = dlsorter_properties.mountdir + "/" + dlsorter_properties.showsremotedir
    for d in os.listdir(remotedir):
        if os.path.isdir(os.path.join(remotedir, d)):
            if re.match(d, inname, re.IGNORECASE):
                outname = d  # We found existing folder and should use this
    if outname == "":
        outname = inname  # No existing folder so we'll use what we have
    return outname


#  Verify each item in the list is a valid type
#  inlist = list of absolute path mkv files
#  outlist = files to be processed and copied
#  rejectlist = files to be placed in tmp location for manual intervention
def verify_types(inlist):
    outlist = []
    rejectlist = []
    for i in inlist:
        if determine_type_by_base_name(i, True):
            outlist.append(i)
        elif determine_type_by_parent_folder_name(i, True):
            repairedfile = repair_file_name(i)
            outlist.append(repairedfile)
        else:
            rejectlist.append(i)
    for o in outlist:
        logging.debug("File to be copied: " + o)
    for r in rejectlist:
        logging.info("Manual intervention required: " + os.path.basename(r))
    return outlist, rejectlist


#  Repair file name by giving it the name of parent folder
#  infile = absolute path mkv file
#  This is only called after it is verified parent folder name is valid to rename to
def repair_file_name(infile):
    outfile = ""
    if "_tmp" not in infile:  # ex: /home/user/dir/abc/123.mkv
        tmp1 = os.path.dirname(infile)  # ex: /home/user/dir/abc
        tmp2 = os.path.basename(tmp1) + "_tmp"  # ex: abc_tmp
        tmpdest = tmp1 + "/" + tmp2  # ex: /home/user/dir/abc/abc_tmp
        dlsorter_os.create_directory(tmpdest)  # ex: /home/user/dir/abc/abc_tmp
        dlsorter_os.copy_file(infile, tmpdest)  # ex: /home/user/dir/abc/123.mkv to /home/user/dir/abc/abc_tmp
        infile = tmpdest + "/" + os.path.basename(infile)  # ex: /home/user/dir/abc/abc_tmp/123.mkv
    tmp1 = os.path.dirname(infile)  # ex: /home/user/dir/abc/abc_tmp
    tmp2 = os.path.basename(tmp1)  # ex: abc_tmp
    tmp3 = tmp2.replace("_tmp", ".mkv")  # ex: abc.mkv
    newfilename = tmp1 + "/" + tmp3  # ex: /home/user/dir/abc/abc_tmp/abc.mkv
    dlsorter_os.rename_file(infile, newfilename)
    outfile = newfilename
    return outfile


#  Determine the temporary destination to extract files to
#  infile = the file name within rar
#  inrar = the rar name that contains the file
def determine_tmpdest_rar(infile, inrar):
    outpath = os.path.dirname(inrar) + "/" # ex: /home/user/dir/
    debuglog = False
    if determine_type_by_base_name(infile, debuglog):  # ex: filename.mkv
        outpath = outpath + infile.replace(".mkv", "_tmp")  # ex: /home/user/dir/file/filename_tmp
    elif determine_type_by_parent_folder_name(inrar, debuglog):  # ex: /home/user/dir/file.rar
        tmp1 = os.path.dirname(inrar)  # ex: /home/user/dir
        tmp2 = os.path.basename(tmp1) + "_tmp"  # ex: dir
        outpath = outpath + tmp2  # ex: /home/user/dir/dir_tmp
    else:
        outpath = outpath + os.path.basename(inrar).replace(".rar", "_tmp")  # ex: /home/user/dir/file_tmp
    return outpath

