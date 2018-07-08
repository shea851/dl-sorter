import dlsorter_properties
import logging
import subprocess


#  Update plex libraries using rest api
#  inlist = list of items in which 3rd index contains type
def update_libraries(inlist):
    types = set()
    for i in inlist:  # Build type set containing only unique types
        types.add(i[3])
    for t in types:
        librarykey = "0"
        if t == "show":
            librarykey = dlsorter_properties.showskey
        elif t == "movie":
            librarykey = dlsorter_properties.movieskey
        else:
            break
        url = "http://" + dlsorter_properties.plexip + ":32400/library/sections/" + librarykey + "/refresh?X-Plex-Token=" + dlsorter_properties.plextoken
        p = subprocess.Popen(['/usr/bin/curl', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode == 0:
            logging.info("Plex: Library update -> " + t + "s")
            logging.debug("Plex: Library update " + t + "s Command -> " + "/usr/bin/curl " + url)
        else:
            logging.error(err)
            logging.error("Plex library update: [FAILURE]")
