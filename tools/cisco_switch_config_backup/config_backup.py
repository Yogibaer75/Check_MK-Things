#!/usr/bin/python

import pexpect, sys, cmd, time, os, getopt

def usage():
    sys.stderr.write("""Check_MK 3par Agent
USAGE: config_backup.py HOST
       config_backup -h

ARGUMENTS:
  HOST                                      Host name or IP address of Cisco Switch

OPTIONS:
  -h, --help                                Show this help message and exit
""")

opt_host = None

short_options = "hh:"
long_options = [ "help" ]

try:
    opts, args = getopt.getopt( sys.argv[1:], short_options, long_options )
except getopt.GetoptError, err:
    sys.stderr.write("%s\n" % err)
    sys.exit(1)

for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
        elif not opt:
            usage()
            sys.exit(0)

if len(args) == 1:
    opt_host = args[0]
elif not args:
    sys.stderr.write("ERROR: No host given.\n")
    sys.exit(1)
else:
    sys.stderr.write("ERROR: Please specify exactly one host.\n")
    sys.exit(1)

def git_command(args):
    encoded_args = " ".join([ a.encode("utf-8") for a in args ])
    command = "cd '%s' && git %s 2>&1" % ("/backup", encoded_args)
    p = os.popen(command)
    output = p.read()
    status = p.close()
    if status != None:
        print("Error executing GIT command %s: %s") % (command.decode('utf-8'), output)

def shell_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"

def do_git_commit():
    author = shell_quote("%s <%s>" % ("OMD site sandvik", "sandvik@DEWRMON01.Schmalkalden@sandvik.com"))
    git_dir = "/backup/.git"
    if not os.path.exists(git_dir):
        git_command(["init"])
        file("/backup/.gitignore", "w").write("!.gitignore\n*swp\n")

        git_command(["add", ".gitignore" ])
        git_command(["commit", "--author", author, "-m", shell_quote(_("Initialized GIT for Backup"))])

    # Only commit, if something is changed
    if os.popen("cd '%s' && git ls-files -om" % "/backup").read().strip():
        git_command(["add", "*"])
        message = "New configuration added"
        git_command(["commit", "--author", author, "-m", shell_quote(message)])

user = '<user>'
password = '<password>'

child = pexpect.spawn ('ssh '+user+'@'+opt_host)
child.maxread=9999999
child.expect ('.*assword:.*')
child.sendline (password)
child.expect ('.*#')
child.sendline ('terminal length 0')
child.expect ('.*#')
fout = file('/backup/'+host+'-running-config.bak','w')
child.logfile_read = fout
child.sendline('show running-config')
child.expect('.*#', timeout=999)
fout.close()
child.sendline('exit')
child.close()
do_git_commit()

sys.stdout.write("Configuration succesfull saved")
sys.exit(0)