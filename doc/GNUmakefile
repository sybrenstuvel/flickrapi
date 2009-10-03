all: index.html

%.html: %.rst documentation.css html4css1.css
	rst2html --stylesheet-path=documentation.css $< $@

clean:
	rm -f flickrapi.html

upload: index.html
	rsync -va documentation.css index.html html4css1.css ../../www.stuvel.eu/htdocs/flickrapi/documentation/

apidoc:
	rm -rf apidoc
	epydoc --docformat=RestructuredText \
		   --name FlickrAPI \
		   --url http://stuvel.eu/projects/flickrapi \
		   --show-sourcecode \
		   --verbose \
		   -o apidoc \
		   flickrapi

.PHONY: clean upload apidoc
