#!/usr/bin/perl
# $Id: check_sepsesam.pl 1562 2009-11-05 12:41:01Z wpreston $
#
#

=pod

=head1 COPYRIGHT

 
This software is Copyright (c) 2009 NETWAYS GmbH, William Preston
                               <support@netways.de>

(Except where explicitly superseded by other copyright notices)

=head1 LICENSE

This work is made available to you under the terms of Version 2 of
the GNU General Public License. A copy of that license should have
been provided with this software, but in any event can be snarfed
from http://www.fsf.org.

This work is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301 or visit their web page on the internet at
http://www.fsf.org.


CONTRIBUTION SUBMISSION POLICY:

(The following paragraph is not intended to limit the rights granted
to you to modify and distribute this software under the terms of
the GNU General Public License and is only of importance to you if
you choose to contribute your changes and enhancements to the
community by submitting them to NETWAYS GmbH.)

By intentionally submitting any modifications, corrections or
derivatives to this work, or any other work intended for use with
this Software, to NETWAYS GmbH, you confirm that
you are the copyright holder for those contributions and you grant
NETWAYS GmbH a nonexclusive, worldwide, irrevocable,
royalty-free, perpetual, license to use, copy, create derivative
works based on those contributions, and sublicense and distribute
those contributions and any derivatives thereof.

Nagios and the Nagios logo are registered trademarks of Ethan Galstad.

=head1 NAME

check_sepsesam

=head1 SYNOPSIS

Shows the status of backup jobs

=head1 OPTIONS

check_sepsesam [options] 

=over

=item   B<--warning>

warning level - if there are less than this number of successful backups then warn

=item   B<--critical>

critical level - if there are less than this number of successful backups then return critical

=item   B<--anyerror>

return critical if any backup was not successful (overrides warning/critical values)

=item   B<--noperfdata>

disable performance data (if graphing is not required)

=item   B<--lastcheck>

The time of the last check in seconds since 1 Jan 1970 (unixtime)

=item   B<--until>

Ignores any backups COMPLETED after this date (in the same format as lastcheck)

=item   B<--host>

The hostname to check.  Multiple values may be separated by commas

=item   B<--task>

The task name to check.  Multiple values may be separated by commas

=back

=head1 DESCRIPTION

This plugin checks the status of backups in the SEP Sesam Database.

It requires that the Sesam init script has been sourced; e.g.
add the following line to /etc/init.d/nagios 
. /var/opt/sesam/var/ini/sesam2000.profile

The plugin checks the status of all backups which match the Host / Task that
have been completed since the last check and delivers the data in multi-line
format.

It is possible to separate multiple hosts and/or tasks with commas.

Backups that are still running will not be included in the results.


=head1 EXAMPLES

check_sepsesam.pl -H host1 -T testbackup -l $LASTSERVICECHECK$

- checks all backups with name testbackup on host1 since the last
check; always returns OK


check_sepsesam.pl -H host1,host2,host3 -T testbackup,fullbackup -l $LASTSERVICECHECK$ -w 2 -c 1

- checks various tasks on host1, host2 and host3.  Returns a warning if less than 2 were successful.
Returns a critical if less than 1 was successful


check_sepsesam.pl -H host1,host2,host3 -T backup -l $LASTSERVICECHECK$ --anyerror

- returns a critical if any of the matching backups failed


check_sepsesam.pl --lastcheck `date -d "yesterday 08:00" +%s` --until `date -d "today 08:00" +%s` --anyerror

- checks all hosts between two dates


=cut

use Data::Dumper;
use Getopt::Long;
use Pod::Usage;
use POSIX;
use Time::Local;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2,'UNKNOWN'=>3,'DEPENDENT'=>4);
my @results;
my %taghash;
my @temparr = split(/\//, $0);
my $filename = $temparr[$#temparr];
my $timestamp = undef;
$timestamp = mktime(localtime());
$timestamp = $timestamp - 86400;
my $sql_bin = 'sm_db.exe';
my $sql_path = '/cygdrive/c/Program Files/SEPsesam/bin/sesam';
my $lastCheck = $timestamp;
my $help = undef;
my $task = undef;
my $errors = 0;
my $warnings = 0;
my $completed = 0;
my $after = '1970-01-01 00:00:00';
my $hostname = '';
my $warn = 0;
my $crit = 0;
my $exitval = 'UNKNOWN';


Getopt::Long::Configure('bundling');
my $clps = GetOptions(

	"l|lastcheck=i"	=> \$lastCheck,
	"u|until=i"	=> \$until,
	"H|host=s"	=> \$hostname,
	"T|task=s"	=> \$task,
	"w|warning=i"	=> \$warn,
	"c|critical=i"	=> \$crit,
	"anyerror!"	=> \$anyerror,
	"n|noperfdata!"	=> \$noperfdata,
	"h|help"    => \$help

);

pod2usage( -verbose => 2, -noperldoc => 1) if ($help);

if ($lastCheck)
{
	# only look for backups newer than the last check
	# lastcheck is time_t
	# N.B. we are assuming that the times in the DB are local times
	$after = timetToIso8601($lastCheck);
}


	

foreach my $i (split(':', $ENV{'PATH'}))
{

	if (-x "$i/$sql_bin")
	{
		$sql_path = $i;
		last;
	}
}

nagexit('UNKNOWN', "Binary not found ($sql_bin).\nMaybe you want to source the init script (/var/opt/sesam/var/ini/sesam2000.profile)?") unless defined($sql_path);

# my $query = "select c.name,l.name as location,r.task,r.start_tim,r.stop_tim,(round((r.blocks/1024.),2) || 'MB') as size,r.throughput,s.state,r.msg from clients as c left join locations as l on c.location=l.id  left join results as r on r.client=c.name left join cal_sheets as s on r.saveset=s.id where r.stop_tim >'".$after."' and (s.state<>'a' or s.state is null)";
# my $query = "select c.name,l.name as location,r.task,r.start_tim,r.stop_tim,(round((r.blocks/1024.),2) || 'MB') as size,r.throughput,r.state,r.msg from clients as c left join locations as l on c.location=l.id  left join results as r on r.client=c.name where r.stop_tim >'".$after."' and r.state<>'a'";
my $query = "select c.name,l.name as location,r.task,r.start_time,r.stop_time,(round((r.blocks/1024.),2) || 'MB') as size,r.throughput,r.state,r.msg from clients as c left join locations as l on c.location=l.id  left join results as r on r.client=c.name where r.stop_time >'".$after."' and r.state<>'a'";

$query .= " and r.stop_time <='".timetToIso8601($until)."'" if ($until);


if ($hostname =~ /,/)
{
	# we have a list of multiple hosts
	my @hostlist = split(',', $hostname);
	$query .= " and c.name in ('".join("','", @hostlist)."')";
}
elsif ($hostname ne '')
{
	$query .= " and c.name ='".$hostname."'";
}

if ($task)
{
	if ($task =~ /,/)
	{
		# we have a list of multiple tasks
		my @tasklist = split(',', $task);
		$query .= " and r.task in ('".join("','", @tasklist)."')";
	}
	else
	{
		$query .= " and r.task ='".$task."'";
	}
}

# print "$sql_path/$sql_bin \"$query\"\n";
my $retval = `"$sql_path/$sql_bin" "$query"`;

nagexit('UNKNOWN', "$sql_path/$sql_bin returned error ".($? >> 8).".\nMaybe you want to source the init script (/var/opt/sesam/var/ini/sesam2000.profile) in your start script?") if ($? gt 0);


foreach my $i (split('\n', $retval))
{
	push (@results, {parseReply($i)}) if ($i =~ /^\|/);
}


foreach my $i (@results)
{
	my $status = convertState($$i{'state'});
	$statusline .= "$status: $$i{'location'}/$$i{'name'}/$$i{'task'} $$i{'start_time'}\n";

	my $size = $$i{'size'};
	$size =~ s/ \/://g;
	$size =~ s/NULL/0MB/;
	

	# The units are actually GB/h but this may cause problems with some grapher addons :-(
	my $throughput = $$i{'throughput'};
	$throughput =~ s/[ \/:]//g;
	$throughput =~ s/NULL/0GBh/;

	$perfdata .= "'".uniqueTag($$i{'name'}."_".$$i{'task'})."_size'=$size;;;; ";
	$perfdata .= "tput=$throughput;;;; ";
#	$perfdata .= "'".uniqueTag($$i{'name'}.'_'.$$i{'task'})." tput'=$throughput;;;; ";
	##########$perfdata .= "'".uniqueTag($$i{'name'}.'_'.$$i{'task'})." duration'=".timeDiffSecs($$i{'start_time'}, $$i{'stop_time'}).";;;; ";


	next if ($status eq 'RUNNING');
        $errors++ if ($status eq 'FAILED' || $status eq 'BROKEN');
        $warnings++ if ($status eq 'UNKNOWN' || $status eq 'WARNING');
        $completed++;
}

################ 2012-10-26 # $perfdata = " sepsesam::check_multi::plugins=$completed time=0.00".$perfdata;


my $retstr = ($completed - $errors)." of $completed backups successful with $warnings warnings";

if ($errors > 0 )
{
        $exitval = 'CRITICAL';
}
elsif (($completed - $errors) < $crit)
{
        $exitval = 'CRITICAL';
}
elsif ($warnings > 0)
{
        $exitval = 'WARNING';
}
else
{
        $exitval = 'OK';
}

$perfdata = '' if ($noperfdata);
nagexit($exitval, "$retstr |$perfdata \n");


sub uniqueTag
{
	my ($tag) = @_;

	$tag =~ s/[^a-zA-Z0-9_\.-]//g;

	my $suffix = '';
	while (exists($taghash{$tag.$suffix}))
	{
		$suffix++;
	}
	$taghash{$tag.$suffix} = '1';
	return ($tag.$suffix);
}


sub parseReply
{
	# Creates a hash from the reply
	
	my ($line) = @_;
	my %out;
	
	for my $i (split('\|', $line))
	{
		$i =~ /([^=]*)=(.*)/ or next;
		$out{$1} = $2;
	}

	return %out;
}

sub nagexit
{
	my $errlevel = shift;
	my $string = shift;

	print "$errlevel: $string\n";
	exit $ERRORS{$errlevel};
}

sub timetToIso8601
{
	# convert a time_t value to YYYY-MM-DD HH:MM:SS

	my ($t) = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($t);
	return (sprintf('%04d-%02d-%02d %02d:%02d:%02d', ($year + 1900), ($mon + 1), $mday, $hour, $min, $sec));
}

sub timeDiffSecs
{
	my ($start, $end) = @_;

	my $timediff=(convert_time($end))-(convert_time($start));
	return (abs($timediff));
}




sub convert_time
{

my $dstr = shift;

my @dat = split(' ',$dstr);

my @datum = reverse(split('-',$dat[0]));
my @uhrzeit = reverse(split(':',$dat[1]));

my $test =  timelocal( @uhrzeit, @datum );
return  $test;

}



sub timeDiff
{
	my ($start, $end) = @_;


	my $timediff=localtime($end)-localtime($start);

	my $days = int($timediff / 86400);
	$timediff = $timediff - ($days * 86400);
	my $hours = int($timediff / 3600);
	$timediff = $timediff - ($hours * 3600);
	my $mins = int($timediff / 60);
	$timediff = $timediff - ($mins * 60);

	return (0) if ($days > 99);

	return (sprintf('%02d:%02d:%02d:%02s', $days, $hours, $mins, $timediff));
}

sub convertState
{
	# convert the sesam state to a suitable return value

	my %stateMap = ( 
		'0' => 'OK',
		'X' => 'FAILED',
		'a' => 'RUNNING',
		'1' => 'WARNING',
		'3' => 'BROKEN'
	);
	my ($state) = @_;
	
	return ($stateMap{$state}) if defined($stateMap{$state});
	return 'UNKNOWN';
}
