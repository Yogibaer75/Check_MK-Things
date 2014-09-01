<?php
#
# check_netappfiler -s cacheage
#
# RRDtool Options
$opt[1] = "--vertical-label \"Cache Age in min\" -l 0 -r --title \"Cache age of $hostname ($servicedesc)\"";
#
#
$def[1] = "";

# Graphen Definitions

$def[1] .= "DEF:cacheage_avg=$rrdfile:$DS[1]:AVERAGE "; 
$def[1] .= "DEF:cacheage_min=$rrdfile:$DS[1]:MIN "; 
$def[1] .= "DEF:cacheage_max=$rrdfile:$DS[1]:MAX "; 

$def[1] .= "AREA:cacheage_max#6666ffcc: ";
$def[1] .= "AREA:cacheage_min#ffffff ";
$def[1] .= "LINE1:cacheage_avg#0000ff:\"Cache age:\" ";
$def[1] .= "GPRINT:cacheage_avg:LAST:\"%3.1lfmin \" ";
$def[1] .= "GPRINT:cacheage_min:MIN:\"(%3.1lfmin -\" ";
$def[1] .= "GPRINT:cacheage_max:MAX:\"%3.1lfmin)\\n\" ";

?>