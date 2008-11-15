all: index.html


%.html: %.rst documentation.css html4css1.css
	rst2html --stylesheet-path=documentation.css $< $@

clean:
	rm -f flickrapi.html

upload: index.html
	rsync -va documentation.css index.html html4css1.css ../../www.stuvel.eu/htdocs/projects/flickrapi/documentation/

.PHONY: clean upload
