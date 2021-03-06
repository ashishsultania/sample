import os
from subprocess import Popen, PIPE
import hashlib
import tarfile
import shutil
import ntpath
import ServerConfig



def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed

def linksubsets(file_new,file_old):
    file_new_ = ''.join(file_new)
    file_old_ = ''.join(file_old)
    flinkdone = 0
    
    if os.path.islink(file_new_) == True:
        file_new = os.path.realpath(file_new_)
    else:
        file_new = file_new_

    if os.path.islink(file_old_) == True:
        file_old = os.path.realpath(file_old_)
    else:
        file_old = file_old_
    
    with open(file_new, 'r') as file1:
        with open(file_old, 'r') as file2:
            if( (set(file2).issubset(file1))) :
                flinkdone = 1
                os.symlink(file_new, file_old+"tmp")
                try:
                    shutil.move(file_old+"tmp",file_old)
                except shutil.Error:
                    pass
    file2.close()
    file1.close()

    if (flinkdone == 0):
        with open(file_new, 'r') as file1:
            with open(file_old, 'r') as file2:
                if( (set(file1).issubset(file2))) :
                    os.symlink(file_old, file_new+"tmp")
                    try:
                        shutil.move(file_new+"tmp",file_new)
                    except shutil.Error:
                        pass
        file2.close()
        file1.close()


def check_for_duplicates(paths, commondir):
    hashes_by_size = {}
    hashes_on_1k = {}
    hashes_full = {}
    singlefiles = {}
    
    if not os.path.isdir(commondir):
        os.mkdir(commondir)
        
    
    for path in paths:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    file_size = os.path.getsize(full_path)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    pass

                duplicate = hashes_by_size.get(file_size)

                # Append to a dictionary of same size list 
                if duplicate:
                    hashes_by_size[file_size].append(full_path)
                # Create and dictionary and append same size list
                else:
                    hashes_by_size[file_size] = []  # create the list for this file size
                    hashes_by_size[file_size].append(full_path)
                  
    # For all files with the same file size, get their hash on the 1st 1024 bytes
    for __, files in hashes_by_size.items():
        #New file or not same
        if len(files) < 2:
            bn = ntpath.basename(files[0])
            if singlefiles.get(bn):
                singlefiles[bn].append(files)
            else:
                singlefiles[bn] = (files)
            
            continue    # this file size is unique, no need to spend cpy cycles on it
      
        
        
        
        for filename in files:
            small_hash = get_hash(filename, first_chunk_only=True)

            duplicate = hashes_on_1k.get(small_hash)
            if duplicate:
                hashes_on_1k[small_hash].append(filename)
            else:
                hashes_on_1k[small_hash] = []          # create the list for this 1k hash
                hashes_on_1k[small_hash].append(filename)

    # For all files with the hash on the 1st 1024 bytes, get their hash on the full file - collisions will be duplicates
    for __, files in hashes_on_1k.items():
        #New file or not same
        if len(files) < 2:
            continue    # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it
        

        for filename in files:
            full_hash = get_hash(filename, first_chunk_only=False)

            duplicate = hashes_full.get(full_hash)
            if duplicate:
                #print "Duplicate found: %s and %s" % (filename, duplicate)
                try:
                    if os.path.islink(duplicate) == True and os.path.getsize(duplicate) != 0:
                        linkto = os.readlink(duplicate)
                        os.symlink(linkto, filename+"tmp")
                        shutil.move(filename+"tmp",filename)
                    else:
                        shutil.copy2(filename, commondir)
                except shutil.Error:
                    pass
                if os.path.islink(duplicate) == False:
                    bn = ntpath.basename(filename)
                    
                    rcd =  os.path.realpath(commondir) + "/" + bn
                    os.symlink(rcd, filename+"tmp")
                    os.symlink(rcd, duplicate+"tmp")
                    try:
                        shutil.move(filename+"tmp",filename)
                        shutil.move(duplicate+"tmp",duplicate)
                    except shutil.Error:
                        pass
                
            else:
                hashes_full[full_hash] = filename
    for key,val in singlefiles.items():
        if len(val) == 2:            
            linksubsets(val[1],val[0])
    

def untar(filename):
    #os.chdir(dirnm)
    #print os.getcwd()
    #print filename
    a, b = filename.split('.tar')
    if not os.path.isdir(a):
        cmd = "mkdir " + a
        p = Popen([cmd], stdin=PIPE, shell=True)
        (output, err) = p.communicate()
 
        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()
        #print "Command output : ", output
        #print "Command exit status/return code : ", p_status

        cmd = "tar -xzf " +  filename + " -C " + a
        p = Popen([cmd], stdin=PIPE, shell=True)
        p.wait()

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def tar(filename,source_dir,dirnm):
    os.chdir(source_dir)
    #print os.getcwd()
    cmd = "tar -czf - * > ../" +filename
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.wait()
    os.chdir(dirnm)


def main():
    #dirnm =  ServerConfig.basedir + '/periodic_log'
    dirnm =  ServerConfig.basedir + '/uploadserver'
        
    if not os.path.isdir(dirnm):
        os.mkdir(dirnm)
    os.chdir(dirnm)

    commondir = 'common/'
    if not os.path.isdir(commondir):
        os.mkdir(commondir)
        
    dated_files = [(os.path.getmtime(fn), os.path.basename(fn)) 
                   for fn in os.listdir(dirnm) if fn.lower().endswith('.tar.gz')]
    dated_files.sort()
    #files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)

    if len(dated_files) == 1:
        return
        exit(0)

    oldest = dated_files[0][1]
    new1   = dated_files[-1][1]
    new2   = dated_files[-2][1]

    #print "Oldest:", oldest
    #print "Newest1:", new1
    #print "Newest2:", new2
    
    untar(new2)
    untar(new1)

    a1, b1 = new2.split('.tar')
    a2, b2 = new1.split('.tar')


    filesindir1 = []
    for path, subdirs, files in os.walk(dirnm+'/'+a1):
        for name in files:
            #print os.path.join(path, name)
            filesindir1.append(os.path.join(path, name))
    #print filesindir1
    #print "....................................."
    filesindir2 = []
    for path, subdirs, files in os.walk(dirnm+'/'+a2):
        for name in files:
            #print os.path.join(path, name)
            filesindir2.append(os.path.join(path, name))
    #print filesindir2
    #print "....................................."



    check_for_duplicates([dirnm+'/'+a1, dirnm+'/'+a2],commondir+"/"+a1+a2)
    tar("tmp1.tar.gz", a1,dirnm)
    tar("tmp2.tar.gz", a2,dirnm)

    shutil.rmtree(dirnm+'/'+a1)
    shutil.rmtree(dirnm+'/'+a2)
    os.remove(new1)
    os.remove(new2)
    os.rename("tmp1.tar.gz",new2)
    os.rename("tmp2.tar.gz",new1)

    list1 = []
    for f in filesindir1:
        w1, l1 = f.split(a1)
        list1.append(l1)
        

    list2 = []
    for f in filesindir2:
        w2, l2 = f.split(a2)
        list2.append(l2)

    namematchindex = [(i, j) for i in range(len(list1)) for j in range(len(list2)) if list1[i] == list2[j]]

    os.chdir(ServerConfig.basedir)


if(__name__ == "__main__"):
    main()

