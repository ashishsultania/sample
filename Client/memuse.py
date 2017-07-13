#!/usr/bin/env python

#   http://github.com/pixelb/scripts/commits/master/scripts/ps_mem.py

import errno
import os
import sys

#   Define some global variables

PAGESIZE = os.sysconf("SC_PAGE_SIZE") / 1024 #KiB
our_pid = os.getpid()

have_pss = 0
have_swap_pss = 0

class Proc:
    def __init__(self):
            self.proc = '/proc'

    def path(self, *args):
        return os.path.join(self.proc, *(str(a) for a in args))

    def open(self, *args):
        return open(self.path(*args))
        
proc = Proc()

def filewrite(filename,text,mode):
    target = open(filename, mode)
    target.write(text)  
    target.close()


def print_header(filename):
    output_string = " Private  +   Shared  =  RAM used"
    output_string += " " * 5 + "Shared Swap"
    output_string += "   Swap used"
    output_string += "\tProgram"
    output_string += "\n\n"
    filewrite(filename,output_string,'w')
    
    
#return Private,Shared
#Note shared is always a subset of rss (trs is not always)
def getMemStats(pid):
    global have_pss
    global have_swap_pss
    mem_id = pid #unique
    Private_lines = []
    Shared_lines = []
    Pss_lines = []
    Rss = (int(proc.open(pid, 'statm').readline().split()[1])
           * PAGESIZE)
    Swap_lines = []
    Swap_pss_lines = []

    Swap = 0
    Swap_pss = 0

    if os.path.exists(proc.path(pid, 'smaps')):  # stat
        lines = proc.open(pid, 'smaps').readlines()  # open
        # Note we checksum smaps as maps is usually but
        # not always different for separate processes.
        mem_id = hash(''.join(lines))
        for line in lines:
            if line.startswith("Shared"):
                Shared_lines.append(line)
            elif line.startswith("Private"):
                Private_lines.append(line)
            elif line.startswith("Pss"):
                have_pss = 1
                Pss_lines.append(line)
            elif line.startswith("Swap:"):
                Swap_lines.append(line)
            elif line.startswith("SwapPss:"):
                have_swap_pss = 1
                Swap_pss_lines.append(line)
        Shared = sum([int(line.split()[1]) for line in Shared_lines])
        Private = sum([int(line.split()[1]) for line in Private_lines])
        #Note Shared + Private = Rss above
        #The Rss in smaps includes video card mem etc.
        if have_pss:
            pss_adjust = 0.5 # add 0.5KiB as this avg error due to truncation
            Pss = sum([float(line.split()[1])+pss_adjust for line in Pss_lines])
            Shared = Pss - Private
        # Note that Swap = Private swap + Shared swap.
        Swap = sum([int(line.split()[1]) for line in Swap_lines])
        if have_swap_pss:
            # The kernel supports SwapPss, that shows proportional swap share.
            # Note that Swap - SwapPss is not Private Swap.
            Swap_pss = sum([int(line.split()[1]) for line in Swap_pss_lines])
    else:
        Shared = int(proc.open(pid, 'statm').readline().split()[2])
        Shared *= PAGESIZE
        Private = Rss - Shared
    return (Private, Shared, mem_id, Swap, Swap_pss)


def getCmdName(pid):
    cmdline = proc.open(pid, 'cmdline').read().split("\0")
    if cmdline[-1] == '' and len(cmdline) > 1:
        cmdline = cmdline[:-1]

    path = proc.path(pid, 'exe')
    try:
        path = os.readlink(path)
        # Some symlink targets were seen to contain NULs
        path = path.split('\0')[0]
    except OSError:
        val = sys.exc_info()[1]
        if (val.errno == errno.ENOENT or # either kernel thread or process gone
            val.errno == errno.EPERM or
            val.errno == errno.EACCES):
            raise LookupError
        raise
    
    if path.endswith(" (deleted)"):
        path = path[:-10]
        if os.path.exists(path):
            path += " [updated]"
        else:
            #The path could be have prelink stuff so try cmdline
            #which might have the full path present. This helped for:
            #/usr/libexec/notification-area-applet.#prelink#.fX7LCT (deleted)
            if os.path.exists(cmdline[0]):
                path = cmdline[0] + " [updated]"
            else:
                path += " [deleted]"
    exe = os.path.basename(path)
    cmd = proc.open(pid, 'status').readline()[6:-1]
    if exe.startswith(cmd):
        cmd = exe 
    return cmd

#Make it readable
def human(num, power="Ki", units=None):
    if units is None:
        powers = ["Ki", "Mi", "Gi", "Ti"]
        while num >= 1000: #4 digits
            num /= 1024.0
            power = powers[powers.index(power)+1]
        return "%.1f %sB" % (num, power)
    else:
        return "%.f" % ((num * 1024) / units)


def cmd_with_count(cmd, count):
    if count > 1:
        return "%s (%u)" % (cmd, count)
    else:
        return cmd


def get_memory_usage(include_self=False):
    cmds    = {}
    shareds = {}
    mem_ids = {}
    count   = {}
    swaps   = {}
    shared_swaps = {}

    # Get all the list of PIds    
    for pid in os.listdir(proc.path('')):
        if not pid.isdigit():
            continue
        pid = int(pid)

        # Some filters        
        if pid == our_pid:
            continue
        try:
            cmd = getCmdName(pid)
        except LookupError:
            #kernel threads don't have exe links or
            #process gone
            continue

        try:
            private, shared, mem_id, swap, swap_pss = getMemStats(pid)
        except RuntimeError:
            continue #process gone
        if shareds.get(cmd):
            if have_pss: #add shared portion of PSS together
                shareds[cmd] += shared
            elif shareds[cmd] < shared: #just take largest shared val
                shareds[cmd] = shared
        else:
            shareds[cmd] = shared
        cmds[cmd] = cmds.setdefault(cmd, 0) + private
        if cmd in count:
            count[cmd] += 1
        else:
            count[cmd] = 1
        mem_ids.setdefault(cmd, {}).update({mem_id: None})

        # Swap (overcounting for now...)
        swaps[cmd] = swaps.setdefault(cmd, 0) + swap
        if have_swap_pss:
            shared_swaps[cmd] = shared_swaps.setdefault(cmd, 0) + swap_pss
        else:
            shared_swaps[cmd] = 0

    # Total swaped mem for each program
    total_swap = 0

    # Total swaped shared mem for each program
    total_shared_swap = 0

    # Add shared mem for each program
    total = 0

    for cmd in cmds:
        cmd_count = count[cmd]
        if len(mem_ids[cmd]) == 1 and cmd_count > 1:
            # Assume this program is using CLONE_VM without CLONE_THREAD
            # so only account for one of the processes
            cmds[cmd] /= cmd_count
            if have_pss:
                shareds[cmd] /= cmd_count
        cmds[cmd] = cmds[cmd] + shareds[cmd]
        total += cmds[cmd]  # valid if PSS available
        total_swap += swaps[cmd]
        if have_swap_pss:
            total_shared_swap += shared_swaps[cmd]

    sorted_cmds = sorted(cmds.items(), key=lambda x:x[1])
    sorted_cmds = [x for x in sorted_cmds if x[1]]

    return sorted_cmds, shareds, count, total, swaps, shared_swaps, \
        total_swap, total_shared_swap





def print_memory_usage(sorted_cmds, shareds, count, total, swaps, total_swap,
                       shared_swaps, total_shared_swap,filename):
    for cmd in sorted_cmds:

        output_string = "%9s + %9s = %9s"
        output_data = (human(cmd[1]-shareds[cmd[0]]),
                       human(shareds[cmd[0]]), human(cmd[1]))
        if have_swap_pss:
            output_string += "\t%9s"
            output_data += (human(shared_swaps[cmd[0]]),)
        output_string += "   %9s"
        output_data += (human(swaps[cmd[0]]),)
        output_string += "\t%s\n"
        output_data += (cmd_with_count(cmd[0], count[cmd[0]]),)

        filewrite(filename,output_string % output_data,'a')
        

    if have_pss:
        if have_swap_pss:
            
            filewrite(filename,"%s\n%s%9s%s%9s%s%9s\n%s\n" %
                             ("-" * 61, " " * 10+"Total-RAMUSED:", human(total), " shswp:",
                              human(total_shared_swap), " swap:",
                              human(total_swap), "=" * 61),'a')
                              
            
        else:
            filewrite(filename,"%s\n%s%9s%s%9s\n%s\n" %
                             ("-" * 45, " " * 10+"Total-RAMUSED:", human(total), " swap:",
                              human(total_swap), "=" * 45),'a')
                   
                   
                              
                              

def getmemuse(filename):
    
    print_header(filename)

    sorted_cmds, shareds, count, total, swaps, shared_swaps, total_swap, \
    total_shared_swap = get_memory_usage()
    
    print_memory_usage(sorted_cmds, shareds, count, total, swaps,
                           total_swap, shared_swaps, total_shared_swap,filename)
