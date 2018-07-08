from datetime import timedelta
import dlsorter_archive
import dlsorter_os
import dlsorter_plex
import dlsorter_properties
import dlsorter_rclone
import dlsorter_types
import logging
import os
import sys
import time
import uuid


torrentbasepath = sys.argv[1]  # Absolute path to torrent file/folder passed in by rtorrent
uniquelogid = str(uuid.uuid4()).split("-")[0]
logging.basicConfig(filename=dlsorter_properties.logfile,
                    filemode='a',
                    format='[%(asctime)s] [' + uniquelogid + '] [%(levelname)s]: %(message)s',
                    datefmt='%c',
                    level=logging.getLevelName(dlsorter_properties.loglevel))


# Exit if this isn't a download dir
def failsafe_quit(path):
    quitbool = True
    for d in dlsorter_properties.downloaddirs:
        if d in path:
            quitbool = False
    if quitbool:
        print "quitting"
        quit()


def build_mkvlist(basepath):
    outlist = []
    if os.path.isfile(basepath) and basepath.endswith(".rar"):
        rartmp = build_rar_tmp_list([basepath])
        dlsorter_archive.unrar(rartmp)
        outlist = dlsorter_os.search_for_files(rartmp[0][1], ".mkv")
        basepath = os.path.dirname(basepath)
    elif os.path.isfile(basepath) and basepath.endswith(".mkv"):
        outlist = [basepath]
        basepath = os.path.dirname(basepath)
    else:  # Handle directories
        rarlist = dlsorter_os.search_for_files(basepath, ".rar")
        rartmplist = build_rar_tmp_list(rarlist)
        dlsorter_archive.unrar(rartmplist)
        outlist = dlsorter_os.search_for_files(basepath, ".mkv")
    return outlist, basepath


def build_src_dst_list(inlist, basepath):
    outlist = []
    dstset = set()
    srcdstlist = []
    for i in inlist:
        src = ""
        dst = ""
        mediatype = dlsorter_types.determine_type_by_base_name(i, False)
        if mediatype == "show":
            showinfo = dlsorter_types.get_show_info(i)
            showname = dlsorter_types.get_existing_show_folder_name(showinfo[0].replace(".", " "))
            showseason = "Season " + showinfo[1]  # Leave leading zero
            src = os.path.basename(i)
            dst = dlsorter_properties.showsremotedir + "/" + showname + "/" + showseason
        elif mediatype == "movie":
            src = os.path.basename(i)
            dst = dlsorter_properties.moviesremotedir
        dstset.add(dst)  # Find unique by adding to set
        srcdstlist.append([src, dst, mediatype])
        dlsorter_os.create_symlink(i, basepath + "/" + os.path.basename(i))
    for d in dstset:  # loop unique destinations
        srcfilenames = []
        srcmediatype = ""
        for s in srcdstlist:
            if d == s[1]:
                srcmediatype = s[2]  # This will set this variable many times but who cares
                srcfilenames.append(s[0])  # build list of all source files for each unique destination
        item = [basepath, srcfilenames, dlsorter_properties.rcloneremote + d, srcmediatype]
        outlist.append(item)
    return outlist


#  Build list of rar files and their extract destinations
#  inlist = absolute path rar files
#  Returns two element list, the first is the rar file, the second is destination
def build_rar_tmp_list(inlist):
    if not inlist:  # Only do stuff if necessary
        return
    outlist = []
    for i in inlist:
        tmpdest = ""
        rarcontents = dlsorter_archive.list_rar_files(i)
        if len(rarcontents) == 1:  # We have 1 mkv in rar, so we have options
            tmpdest = dlsorter_types.determine_tmpdest_rar(rarcontents[0], i)
        else:  # We have multiple mkv in rar, so we have no options
            tmp1 = os.path.splitext(i)[0]  # ex: /home/user/dir/file
            tmpdest = tmp1 + "/" + os.path.basename(tmp1) + "_tmp"
        outlist.append([i, tmpdest])
    return outlist


#  Stage these files for later manual intervention
#  inlist = list of absolute path files
def handle_rejects(inlist):
    for i in inlist:
        destination = ""
        if os.path.dirname(i) in dlsorter_properties.downloaddirs:  # This means crap name file had no folder
            destination = dlsorter_properties.stagedir
        else:  # This means crap name file was in a folder and should keep that folder in stagedir
            destination = dlsorter_properties.stagedir + "/" + os.path.basename(os.path.dirname(i))
        if not destination == dlsorter_properties.stagedir:
            dlsorter_os.delete_directory(destination)
            dlsorter_os.create_directory(destination)
        if "_tmp" in i:
            dlsorter_os.move_file(i, destination)
            dlsorter_os.delete_directory(os.path.dirname(i))
        else:
            dlsorter_os.copy_file(i, destination)


def delete_tmp_directories(inlist):
    for i in inlist:  # /home/user/dir/dir_tmp/abc.mkv
        tmp1 = i
        if os.path.isfile(i):
            tmp1 = os.path.dirname(i)  # /home/user/dir/dir_tmp
        if tmp1.endswith("_tmp"):
            dlsorter_os.delete_directory(tmp1)


def remove_symlinks(basepath):
    if os.path.isdir(basepath):
        for f in os.listdir(basepath):
            if f.endswith(".mkv"):
                dlsorter_os.delete_symlink(os.path.join(basepath, f))


def main(basepath):
    failsafe_quit(basepath)
    # irc = subprocess.Popen(["python","ircLogger.py"])
    # time.sleep(2)
    start = time.time()
    logging.info("Start: " + basepath)
    mkvlist, srcpath = build_mkvlist(basepath)
    verifiedlist, rejectlist = dlsorter_types.verify_types(mkvlist)  # Verify/fix filenames
    copylist = build_src_dst_list(verifiedlist, srcpath)  # Build list for rclone copy
    dlsorter_rclone.rclone_copy(copylist)
    dlsorter_plex.update_libraries(copylist)
    handle_rejects(rejectlist)
    remove_symlinks(srcpath)
    delete_tmp_directories(verifiedlist)  # Delete "known" tmp folders
    delete_tmp_directories(dlsorter_os.search_for_folders(basepath, "_tmp"))  # Delete any rogue tmp folders
    end = time.time()
    elapsed = str(timedelta(seconds=(end - start))).split(".")[0]
    logging.info("Finish: [" + elapsed + "] " + basepath)
    # time.sleep(1)  # Ensure we finish logging before we kill stuff
    # irc.send_signal(SIGINT)
    # irc.wait()


main(torrentbasepath)
