rcloneremote = "your-rclone-mount:"  # Unencrypted view of your rclone remote
downloaddirs = ['/home/user/downloads/manual',  # Run against these dirs only
                '/home/user/downloads/auto']    # Format: ['/dir/path1','/dir/path2']
mountdir = "/home/user/mounts/your-mount"  # Mount directory that contains shows/movies directories
stagedir = "/home/user/downloads/tmp"  # This is where poorly named files go
moviesremotedir = "Movies"  # Directory name of movies folder on rclone remote
showsremotedir = "TV Shows"  # Directory name of shows folder on rclone remote
logfile = "/home/user/dlsorter_out.log"
loglevel = "INFO"  # Default "INFO". Change to "DEBUG" to see more informative output
rclonestatslogging = True  # Set to True if you want to see log output like: "21% done, 12.347 Mbytes/s, ETA: 11m55s"
rclonestatsinterval = "5m"  # OOB default is 1m.  5m reduces log spam but still provides updates.
ossearchmkvminsz = 209715200  # 209715200 (200M) should avoid finding any sample files
#  Run command to find library keys: curl http://{IP}:32400/library/sections?X-Plex-Token={TOKEN}
plexip = "8.8.8.8"
plextoken = "token"
movieskey = "1"
showskey = "2"
