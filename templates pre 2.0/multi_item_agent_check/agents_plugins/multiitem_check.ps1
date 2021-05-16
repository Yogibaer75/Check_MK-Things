"<<<checkname>>>"
for ($i = 1; $i -le 10; $i++) {
 $status = Get-Random -Minimum 0 -Maximum 4
 "item$i $status this is a sample plugin with multiple items"
}
