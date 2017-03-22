#!/usr/bin/perl -w

# Copyright (C) 2006, NETWAYS GmbH, Gerd Mueller
# $Id: call.pl 1418 2006-09-25 14:26:22Z gmueller $
# changed to picotts - Andreas Doehler 2016

use Getopt::Long;
use vars qw($opt_n $opt_h $opt_m $opt_c $opt_H $opt_S $opt_C $PROGNAME);

my $tmp="/tmp/";
my $filename="$$";
my $asterisk_sounds="/var/lib/asterisk/sounds/voicealerts/";
my $asterisk_spool="/var/spool/asterisk/outgoing/";
my $sox="/usr/bin/sox ".$tmp.$filename.".wav -t wav -r 8000 - > ".$asterisk_sounds.$filename.".wav";
my $unlink="/usr/bin/unlink ".$tmp.$filename.".wav";

$PROGNAME = "call.pl";

sub print_help($);

Getopt::Long::Configure('bundling');
GetOptions
        ("c:s" => \$opt_c, "contact"    => \$opt_c,
         "C:s" => \$opt_C, "channel"    => \$opt_C,
         "H:s" => \$opt_H, "host"       => \$opt_H,
         "S:s" => \$opt_S, "service"    => \$opt_S,
         "m:s" => \$opt_m, "message"    => \$opt_m,
         "h"   => \$opt_h, "help"       => \$opt_h);

#while(<STDIN>) {
# $opt_m.=lc $_;
#}

print_help ("") if($opt_h);
($opt_c) || print_help("No contact specified\n");
($opt_m) || print_help("No message specified\n");
($opt_C) || print_help("No channel specified\n");
($opt_H) || print_help("No Host specified\n");

my $syntax='/usr/bin/pico2wave -l=de-DE -w='.$tmp.$filename.'.wav "'.$opt_m.'"';

system($syntax);
system("$sox");
system("$unlink");

my $output="";
$output.="Channel: $opt_C\n";
$output.="MaxRetries: 2\n";
$output.="RetryTime: 60\n";
$output.="WaitTime: 30\n";
$output.="Context: Voicealerts\n";
$output.="Extension: s\n";
$output.="Priority: 1\n";
$output.="Callerid: 12345\n";
$output.="Set: MSG=voicealerts/".$filename."\n";
$output.="Set: CONTACT=$opt_c\n";
$output.="Set: HOST=".$opt_H."\n";
$output.="Set: SERVICE=$opt_S\n";
open(OUT,"> ".$asterisk_spool.$filename.".call");
print OUT $output;
close(OUT);

exit 0;

sub print_help ($) {
        my ($message) =@_;
        print "Usage: $PROGNAME -c <contact> -m <message> -C <channel> -H <host> -S <service>\n";
        print $message."\n";
        exit 0;
}

