# all: 
# 	rm -rf /cs/home/hxiao/public_html/figures/
# 	cp -r figures/ /cs/home/hxiao/public_html
# 	chmod -R a+xr /cs/home/hxiao/public_html/figures


all: rm_public_html html_data
	chmod -R a+xr /cs/home/hxiao/public_html/event_html

rm_public_html:
	rm -rf /cs/home/hxiao/public_html/event_html/

html_data:
	cp -r html/ /cs/home/hxiao/public_html/event_html/
	cp -r html/*.html /cs/home/hxiao/public_html/event_html/
	cp -r html/js /cs/home/hxiao/public_html/event_html/
