<?php
$opt[1] = " --slope-mode --vertical-label \"Ops per sec\" -b 1000 --title \"CIFS Statistics for $hostname\" ";
$def[1] = "DEF:total_ops=$rrdfile:$DS[1]:AVERAGE " ;
$def[1] .= "DEF:total_calls=$rrdfile:$DS[2]:AVERAGE " ;
$def[1] .= "DEF:bad_calls=$rrdfile:$DS[3]:AVERAGE " ;
$def[1] .= "DEF:get_attrs=$rrdfile:$DS[4]:AVERAGE " ;
$def[1] .= "DEF:reads=$rrdfile:$DS[5]:AVERAGE " ;
$def[1] .= "DEF:writes=$rrdfile:$DS[6]:AVERAGE " ;
$def[1] .= "DEF:locks=$rrdfile:$DS[7]:AVERAGE " ;
$def[1] .= "DEF:opens=$rrdfile:$DS[8]:AVERAGE " ;
$def[1] .= "DEF:dirops=$rrdfile:$DS[9]:AVERAGE " ;
$def[1] .= "DEF:others=$rrdfile:$DS[10]:AVERAGE " ;
# Total Ops
$def[1] .= "LINE1:total_ops#003300:\"total ops\" " ;
$def[1] .= "GPRINT:total_ops:LAST:\"  last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:total_ops:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:total_ops:MAX:\"max\: %7.2lf ops\\n\" ";
# Total Calls
$def[1] .= "LINE1:total_calls#ff309b:\"total calls\" " ;
$def[1] .= "GPRINT:total_calls:LAST:\"last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:total_calls:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:total_calls:MAX:\"max\: %7.2lf ops\\n\" ";
# Bad Calls
$def[1] .= "LINE1:bad_calls#ff0000:\"bad calls\" " ;
$def[1] .= "GPRINT:bad_calls:LAST:\"  last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:bad_calls:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:bad_calls:MAX:\"max\: %7.2lf ops\\n\" ";
# Get Attrs
$def[1] .= "LINE1:get_attrs#00803b:\"get attrs\" " ;
$def[1] .= "GPRINT:get_attrs:LAST:\"  last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:get_attrs:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:get_attrs:MAX:\"max\: %7.2lf ops\\n\" ";
# Reads
$def[1] .= "LINE1:reads#003bff:\"reads\" " ;
$def[1] .= "GPRINT:reads:LAST:\"      last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:reads:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:reads:MAX:\"max\: %7.2lf ops\\n\" ";
# Writes
$def[1] .= "LINE1:writes#00ff04:\"writes\" " ;
$def[1] .= "GPRINT:writes:LAST:\"     last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:writes:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:writes:MAX:\"max\: %7.2lf ops\\n\" ";
# Locks
$def[1] .= "LINE1:locks#ff8c00:\"locks\" " ;
$def[1] .= "GPRINT:locks:LAST:\"      last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:locks:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:locks:MAX:\"max\: %7.2lf ops\\n\" ";
# Opens
$def[1] .= "LINE1:opens#c0c600:\"opens\" " ;
$def[1] .= "GPRINT:opens:LAST:\"      last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:opens:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:opens:MAX:\"max\: %7.2lf ops\\n\" ";
# Dirops
$def[1] .= "LINE1:dirops#bf2bff:\"dirops\" " ;
$def[1] .= "GPRINT:dirops:LAST:\"     last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:dirops:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:dirops:MAX:\"max\: %7.2lf ops\\n\" ";
# Others
$def[1] .= "LINE1:others#6dacff:\"others\" " ;
$def[1] .= "GPRINT:others:LAST:\"     last\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:others:AVERAGE:\"avg\: %7.2lf ops\" " ;
$def[1] .= "GPRINT:others:MAX:\"max\: %7.2lf ops\\n\" ";
?>