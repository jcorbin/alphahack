alphalist.txt: nwl2023.txt alphanope.txt
	grep -vFf $(word 2,$^) $< >$@

