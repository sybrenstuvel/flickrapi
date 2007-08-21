all: documentation.html


%.html: %.rst %.css html4css1.css
	rst2html --stylesheet-path=documentation.css $< $@

clean:
	rm -f documentation.html

upload: documentation.html
	rsync -va documentation.css documentation.html html4css1.css flickrapi.sf.net:/home/groups/f/fl/flickrapi/htdocs

.PHONY: clean upload
