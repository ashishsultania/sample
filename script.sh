while inotifywait -e CREATE,CLOSE_WRITE,DELETE,MODIFY,MOVED_FROM,MOVED_TO /home/sultana1/dir1/ /home/sultana1/dir3/; do
    rsync -avz /home/sultana1/dir1/ /home/sultana1/dir2/
    rsync -avz /home/sultana1/dir3/ /home/sultana1/dir2/
done
