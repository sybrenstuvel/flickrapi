all: flickrapi.html


%.html: %.rst documentation.css html4css1.css
	rst2html --stylesheet-path=documentation.css $< $@

clean:
	rm -f flickrapi.html

upload: flickrapi.html
	rsync -va documentation.css flickrapi.html html4css1.css flickrapi.sf.net:/home/groups/f/fl/flickrapi/htdocs

.PHONY: clean upload
