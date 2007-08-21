all: documentation.html


%.html: %.rst %.css html4css1.css
	rst2html --stylesheet-path=documentation.css $< $@

clean:
	rm -f documentation.html

.PHONY: clean
