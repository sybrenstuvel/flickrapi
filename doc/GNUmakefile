all: documentation.html


%.html: %.rst
	rst2html $< $@

clean:
	rm -f documentation.html

.PHONY: clean
