"<<<checkname>>>"
for ($i=1; $i -le 10; $i++) {
 $status = get-random -minimum 0 -maximum 4
 "item$i $status this is a sample plugin with multiple items"
}
